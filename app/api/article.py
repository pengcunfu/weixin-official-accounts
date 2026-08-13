from flask import Blueprint
from app.decorator.auth import login_required
from app.decorator.exception import catch_exceptions
from app.utils.json_result import success
from app.models.article import Article
from app.models.public_account import PublicAccount
from app.extensions.database import db
import os
from datetime import datetime
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from app.extensions.docx_process import docx_process
from app.extensions.wechat import WeChatDraft
from app.utils.validate import validate_form
from app.utils.model_helper import update_model_fields
from app.form.article import (
    ArticleListForm, CreateArticleForm, UpdateArticleForm, UpdateArticleContentForm
)
from app.extensions.loger import get_logger

article_bp = Blueprint('article', __name__, url_prefix='/api/article')

# 获取日志记录器
logger = get_logger(__name__)


@article_bp.route('/list', methods=['GET'])
@catch_exceptions
@login_required
def get_articles():
    """获取文章列表"""
    # 表单验证
    form = validate_form(ArticleListForm)

    query = Article.query

    if form.title.data:
        query = query.filter(Article.title.contains(form.title.data))
    if form.category.data:
        query = query.filter(Article.category == form.category.data)

    # 分页
    pagination = query.paginate(
        page=form.page.data,
        per_page=form.limit.data,
        error_out=False
    )

    # 使用模型的to_dict方法
    articles = [article.to_dict() for article in pagination.items]

    return success({
        'data': articles,
        'total': pagination.total,
        'page': form.page.data,
        'limit': form.limit.data
    })


@article_bp.route('/<int:article_id>', methods=['GET'])
@catch_exceptions
@login_required
def get_article(article_id):
    """获取单个文章详情"""
    article = Article.query.get_or_404(article_id)
    return success(article.to_dict())


@article_bp.route('/create', methods=['POST'])
@catch_exceptions
@login_required
def create_article():
    """创建文章"""

    # 表单验证
    form = validate_form(CreateArticleForm)

    # 创建新文章记录
    new_article = Article(
        title=form.title.data or form.original_name.data or '未命名文章',
        category=form.category.data or '默认',
        file_type=form.file_type.data or 'docx',
        file_path=form.path.data,
        cover_path=form.cover_path.data,
        status=form.status.data or '草稿',
        saved_status=form.saved_status.data or '未存稿',
        public_account_nickname=form.public_account_nickname.data,
        author_nickname=form.author_nickname.data,
        uploader_phone=form.uploader_phone.data
    )

    db.session.add(new_article)
    db.session.commit()

    logger.info(f"创建新文章成功: ID={new_article.id}, 标题={new_article.title}")

    return success({
        'id': new_article.id,
        'title': new_article.title
    }, '文章创建成功')


@article_bp.route('/<int:article_id>', methods=['PUT'])
@catch_exceptions
@login_required
def update_article(article_id):
    """更新文章"""

    article = Article.query.get_or_404(article_id)

    # 表单验证
    form = validate_form(UpdateArticleForm)

    # 使用通用更新函数，排除不需要的字段
    update_model_fields(
        model=article,
        form=form,
        exclude_fields=['csrf_token'],  # 排除CSRF令牌
        auto_update_time=True  # 自动更新时间戳
    )

    db.session.commit()

    logger.info(f"更新文章成功: ID={article_id}, 标题={article.title}")
    return success(message='文章更新成功')


@article_bp.route('/<article_ids>', methods=['DELETE'])
@catch_exceptions
@login_required
def delete_article(article_ids):
    """删除文章（支持单个或批量删除）"""

    # 解析ID列表（支持单个ID或逗号分隔的多个ID）
    try:
        if ',' in article_ids:
            # 批量删除
            ids = [int(id.strip())
                   for id in article_ids.split(',') if id.strip()]
        else:
            # 单个删除
            ids = [int(article_ids)]
    except ValueError:
        raise ValueError('无效的文章ID格式')

    if not ids:
        raise ValueError('请提供要删除的文章ID')

    # 获取要删除的文章
    articles = Article.query.filter(Article.id.in_(ids)).all()

    if not articles:
        raise ValueError('未找到要删除的文章')

    # 删除文件和封面
    for article in articles:
        if article.file_path and os.path.exists(article.file_path):
            os.remove(article.file_path)
        if article.cover_path and os.path.exists(article.cover_path):
            os.remove(article.cover_path)

    # 删除数据库记录
    Article.query.filter(Article.id.in_(ids)).delete(
        synchronize_session='fetch')
    db.session.commit()

    logger.info(f"删除文章成功: 数量={len(articles)}, IDs={ids}")

    # 返回适当的消息
    if len(articles) == 1:
        return success(message='文章删除成功')
    else:
        return success(message=f'成功删除 {len(articles)} 篇文章')


@article_bp.route('/<int:article_id>/content', methods=['GET'])
@catch_exceptions
@login_required
def get_article_content(article_id):
    """获取文章内容"""

    article = Article.query.get_or_404(article_id)

    # 优先使用已解析的HTML内容
    if article.content_html:
        return success({'content': article.content_html})

    if not article.file_path:
        raise ValueError('文档不存在')

    file_path = article.file_path
    if not os.path.exists(file_path):
        raise FileNotFoundError('文档文件不存在')

    # 使用docx_process重新解析文档
    try:
        parse_result = docx_process.parse_docx(
            file_path, upload_dir='/uploads')

        if parse_result['status'] == 'success':
            content = parse_result['content_html']
            # 更新文章记录
            article.content_html = content
            article.word_count = parse_result['word_count']
            article.set_images_info(parse_result['images_info'])
            db.session.commit()

            logger.info(
                f"文档解析并更新成功: ID={article_id}, 字数={parse_result['word_count']}")
            return success({'content': content})
        else:
            # 解析失败，使用简单方法
            doc = Document(file_path)
            html_content = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    if paragraph.style.name.startswith('Heading'):
                        level = paragraph.style.name[-1]
                        html_content.append(
                            f'<h{level}>{paragraph.text}</h{level}>')
                    else:
                        align = ''
                        if paragraph.alignment == WD_PARAGRAPH_ALIGNMENT.CENTER:
                            align = ' style="text-align:center"'
                        elif paragraph.alignment == WD_PARAGRAPH_ALIGNMENT.RIGHT:
                            align = ' style="text-align:right"'

                        formatted_text = ''
                        for run in paragraph.runs:
                            text = run.text
                            if run.bold:
                                text = f'<strong>{text}</strong>'
                            if run.italic:
                                text = f'<em>{text}</em>'
                            if run.underline:
                                text = f'<u>{text}</u>'
                            formatted_text += text

                        html_content.append(f'<p{align}>{formatted_text}</p>')

            content = '\n'.join(html_content)
            return success({'content': content})

    except Exception as e:
        raise ValueError(f'文档解析失败: {str(e)}')


@article_bp.route('/<int:article_id>/content', methods=['PUT'])
@catch_exceptions
@login_required
def update_article_content(article_id):
    """更新文章内容"""

    article = Article.query.get_or_404(article_id)

    # 表单验证
    form = validate_form(UpdateArticleContentForm)

    # 更新文章标题
    if form.title.data:
        article.title = form.title.data

    # 保存HTML内容到数据库
    article.content_html = form.content.data

    # 计算字数（去除HTML标签）
    article.word_count = docx_process.count_words(form.content.data)

    # 如果有docx文件路径，也更新docx文件
    if article.file_path:
        try:
            # 使用HTML处理器转换为DOCX
            doc = docx_process.html_to_docx(form.content.data)

            # 保存文档
            file_path = article.file_path
            doc.save(file_path)

        except Exception as docx_e:
            logger.warning(f"保存docx文件失败: {str(docx_e)}")
            # docx保存失败不影响HTML内容保存

    article.updated_time = datetime.utcnow()
    db.session.commit()

    logger.info(f"更新文章内容成功: ID={article_id}, 标题={article.title}")
    return success(message='内容保存成功')


@article_bp.route('/<int:article_id>/save_to_account', methods=['POST'])
@catch_exceptions
@login_required
def save_to_account(article_id: int):
    """将单个文章存储到公众号草稿箱"""

    # 获取文章
    article = Article.query.get(article_id)
    if not article:
        raise ValueError('未找到指定的文章')

    # 检查文章是否关联了公众号
    if not article.public_account_id:
        raise ValueError('文章未关联公众号，无法存储到草稿箱')

    # 获取关联的公众号
    account = PublicAccount.query.filter_by(
        id=article.public_account_id).first()
    if not account:
        raise ValueError('未找到关联的公众号')

    # 检查公众号是否已授权
    if not account.authorized:
        raise ValueError('公众号未授权，无法存储到草稿箱')

    # 获取公众号的微信API凭据
    app_id = account.account_appID
    app_secret = account.app_secret

    # 使用公众号的凭据初始化微信草稿箱API
    api = WeChatDraft(app_id=app_id, app_secret=app_secret)

    # 使用save_to_account方法，返回元组格式 (bool, str)
    success_, message = api.save_to_account(article, account)

    if success_:
        logger.info(
            f"文章存储到草稿箱成功: ID={article.id}, 标题={article.title}, MediaID={article.draft_media_id}")

        # 提交数据库更改
        db.session.commit()

        result = {
            'article_id': article.id,
            'title': article.title,
            'status': 'success',
            'media_id': article.draft_media_id,
            'message': message
        }
        return success(result, f'文章已成功存储到公众号草稿箱！Media ID: {article.draft_media_id}')
    else:
        logger.error(
            f"文章存储到草稿箱失败: ID={article.id}, 标题={article.title}, 错误={message}")

        result = {
            'article_id': article.id,
            'title': article.title,
            'status': 'error',
            'message': message
        }
        return success(result, f'存储失败: {message}')


@article_bp.route('/accounts', methods=['GET'])
@catch_exceptions
@login_required
def get_available_accounts():
    """获取可用的公众号列表"""

    accounts = PublicAccount.query.filter_by(
        authorized=True,
        deleted_time=None
    ).all()

    # 只返回需要的字段
    data = [
        {
            'id': account.id,
            'nickname': account.nickname,
            'account_appID': account.account_appID
        }
        for account in accounts
    ]

    return success(data)
