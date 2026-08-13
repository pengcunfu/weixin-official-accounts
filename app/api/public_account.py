from flask import Blueprint
from app.decorator.auth import login_required
from app.decorator.exception import catch_exceptions
from app.utils.json_result import success, error
from app.models.public_account import PublicAccount
from app.extensions.database import db
from datetime import datetime
from app.extensions.wechat import wechat_auth, wechat_data, WeChatData
from app.utils.validate import validate_form
from app.utils.model_helper import update_model_fields
from app.form.public_account import (
    AccountListForm, CreateAccountForm, UpdateAccountForm,
    AuthStatusForm, ValidateCredentialsForm
)
from app.extensions.loger import get_logger

public_account_bp = Blueprint('accounts', __name__, url_prefix='/api/account')

# 获取日志记录器
logger = get_logger(__name__)


# RESTful API 路由
@public_account_bp.route('/list', methods=['GET'])
@catch_exceptions
@login_required
def get_accounts():
    """获取公众号账号列表"""
    # 表单验证
    form = validate_form(AccountListForm)

    # 只查询未删除的记录
    query = PublicAccount.query.filter_by(deleted_time=None)
    logger.debug(
        f"获取公众号列表: 页码={form.page.data}, 每页数量={form.limit.data}, 昵称过滤={form.nickname.data or '无'}")

    if form.nickname.data:
        query = query.filter(
            PublicAccount.nickname.like(f'%{form.nickname.data}%'))

    total = query.count()
    accounts = query.order_by(PublicAccount.id.desc()).offset(
        (form.page.data - 1) * form.limit.data).limit(form.limit.data).all()

    # 使用模型的to_dict方法
    result = [account.to_dict() for account in accounts]

    logger.info(f"获取公众号列表成功: 总数={total}, 当前页={len(result)}")
    return success({
        'data': result,
        'total': total,
        'page': form.page.data,
        'limit': form.limit.data
    })


@public_account_bp.route('/create', methods=['POST'])
@catch_exceptions
@login_required
def create_account():
    """创建公众号账号"""
    # 表单验证
    form = validate_form(CreateAccountForm)

    logger.info(f"尝试创建公众号账号: AppID={form.account_appID.data}")

    try:
        # 首先验证凭据并获取公众号信息
        account_info = wechat_data.sync_account_info(
            form.account_appID.data, form.appsecret.data)

        # 创建新的公众号记录，使用同步获取的信息
        new_account = PublicAccount(
            account_appID=form.account_appID.data,
            app_secret=form.appsecret.data,
            auth_type='manual',
            authorized=True,
            notes=form.notes.data or '',
            # 从微信API获取的信息
            nickname=account_info.get('nickname', ''),
            head_image=account_info.get('head_image', ''),
            service_type=account_info.get('service_type', 0),
            verify_type=account_info.get('verify_type', 0),
            username=account_info.get('username', ''),
            principal_name=account_info.get('principal_name', ''),
            alias=account_info.get('alias', ''),
            qrcode_url=account_info.get('qrcode_url', ''),
            draft_count=account_info.get('draft_count', 0),
            total_revenue=account_info.get('total_revenue', 0.0),
            yesterday_revenue=account_info.get('yesterday_revenue', 0.0)
        )

        db.session.add(new_account)
        db.session.commit()

        logger.info(
            f"公众号账号创建成功: ID={new_account.id}, 昵称={new_account.nickname}, AppID={new_account.account_appID}")
        return success({
            'id': new_account.id,
            'nickname': new_account.nickname,
            'account_appID': new_account.account_appID
        }, '账号创建成功')

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"公众号账号创建失败: AppID={form.account_appID.data}, 错误={str(e)}")
        raise ValueError(f'创建账号失败: {str(e)}')


@public_account_bp.route('/<int:account_id>', methods=['GET'])
@catch_exceptions
@login_required
def get_account(account_id):
    """获取单个公众号账号详情"""
    account = PublicAccount.query.filter_by(
        id=account_id, deleted_time=None).first()
    if not account:
        logger.warning(f"获取公众号详情失败: ID={account_id}, 原因=账号不存在")
        raise ValueError('账号不存在')

    logger.info(f"获取公众号详情成功: ID={account_id}, 昵称={account.nickname}")
    return success(account.to_dict())


@public_account_bp.route('/<int:account_id>', methods=['PUT'])
@catch_exceptions
@login_required
def update_account(account_id):
    """更新公众号账号"""
    account = PublicAccount.query.filter_by(
        id=account_id, deleted_time=None).first()
    if not account:
        logger.warning(f"更新公众号失败: ID={account_id}, 原因=账号不存在")
        raise ValueError('账号不存在')

    # 表单验证
    form = validate_form(UpdateAccountForm)
    form.account_id = account_id  # 设置账号ID用于唯一性验证

    logger.info(f"尝试更新公众号账号: ID={account_id}")

    # 检查关键字段是否发生变化
    old_app_id = account.account_appID
    old_secret = account.app_secret

    # 使用通用更新函数，将appsecret映射到app_secret字段
    update_model_fields(
        model=account,
        form=form,
        exclude_fields=['csrf_token', 'account_id', 'appsecret'],  # 排除不需要的字段
        auto_update_time=False  # 手动管理时间戳
    )

    # 手动处理appsecret字段映射
    if form.appsecret.data:
        account.app_secret = form.appsecret.data

    # 设置固定字段
    account.auth_type = 'manual'
    account.updated_time = datetime.utcnow()

    # 检查appID或secret是否发生了变化
    app_id_changed = (old_app_id != account.account_appID)
    secret_changed = (old_secret != account.app_secret)

    # 如果更新了appID或secret，尝试同步公众号信息
    if app_id_changed or secret_changed:
        try:
            # 使用WeChatAPI同步账户信息
            wechat_data.sync_account_model(account)
        except Exception as sync_error:
            logger.warning(
                f"公众号信息同步失败: ID={account_id}, AppID={account.account_appID}, 错误={str(sync_error)}")
            # 同步失败不影响更新

    db.session.commit()

    logger.info(
        f"公众号账号更新成功: ID={account_id}, 昵称={account.nickname}, AppID={account.account_appID}")
    return success(message='账号更新成功')


@public_account_bp.route('/<account_ids>', methods=['DELETE'])
@catch_exceptions
@login_required
def delete_account(account_ids):
    """删除公众号账号（软删除）- 支持单个和批量删除"""

    # 解析账号ID，支持单个ID或逗号分隔的多个ID
    try:
        if ',' in str(account_ids):
            # 批量删除：解析逗号分隔的ID
            id_list = [int(id.strip())
                       for id in str(account_ids).split(',') if id.strip()]
        else:
            # 单个删除
            id_list = [int(account_ids)]
    except ValueError:
        logger.warning(f"公众号删除失败: 账号ID格式错误 - {account_ids}")
        raise ValueError('账号ID格式错误')

    if not id_list:
        logger.warning("公众号删除失败: 账号ID不能为空")
        raise ValueError('账号ID不能为空')

    # 查找要删除的账号
    accounts_to_delete = PublicAccount.query.filter(
        PublicAccount.id.in_(id_list),
        PublicAccount.deleted_time == None
    ).all()

    if not accounts_to_delete:
        logger.warning(f"公众号删除失败: 没有找到要删除的账号 - IDs={id_list}")
        raise ValueError('没有找到要删除的账号')

    # 获取实际要删除的账号ID列表
    actual_account_ids = [account.id for account in accounts_to_delete]

    # 批量软删除
    now = datetime.utcnow()
    db.session.query(PublicAccount).filter(
        PublicAccount.id.in_(actual_account_ids),
        PublicAccount.deleted_time == None
    ).update({PublicAccount.deleted_time: now}, synchronize_session='fetch')

    db.session.commit()

    logger.info(
        f"公众号账号删除成功: 数量={len(actual_account_ids)}, IDs={actual_account_ids}")

    # 根据删除的数量返回不同的消息
    if len(actual_account_ids) == 1:
        return success(message='账号删除成功')
    else:
        return success(message=f'成功删除 {len(actual_account_ids)} 个账号')


@public_account_bp.route('/<account_ids>/sync', methods=['POST'])
@catch_exceptions
@login_required
def sync_account_info(account_ids):
    """同步公众号信息 - 支持单个和批量同步"""

    # 解析账号ID，支持单个ID或逗号分隔的多个ID
    try:
        if ',' in str(account_ids):
            # 批量同步：解析逗号分隔的ID
            id_list = [int(id.strip())
                       for id in str(account_ids).split(',') if id.strip()]
        else:
            # 单个同步
            id_list = [int(account_ids)]
    except ValueError:
        logger.warning(f"公众号同步失败: 账号ID格式错误 - {account_ids}")
        raise ValueError('账号ID格式错误')

    if not id_list:
        logger.warning("公众号同步失败: 账号ID不能为空")
        raise ValueError('账号ID不能为空')

    # 查找要同步的账号
    accounts = PublicAccount.query.filter(
        PublicAccount.id.in_(id_list),
        PublicAccount.deleted_time == None
    ).all()

    if not accounts:
        logger.warning(f"公众号同步失败: 没有找到要同步的账号 - IDs={id_list}")
        raise ValueError('没有找到要同步的账号')

    results = []
    success_count = 0

    logger.info(f"开始批量同步公众号信息: 数量={len(accounts)}, IDs={id_list}")

    for account in accounts:
        try:
            # 获取综合信息
            comprehensive_info = wechat_data.get_comprehensive_info()
            formatted_info = wechat_data.format_account_info(comprehensive_info)

            # 更新公众号信息
            account.nickname = formatted_info['nickname']
            account.head_image = formatted_info['head_img']
            account.service_type = comprehensive_info['basic_info'].get(
                'service_type_info', {}).get('id', 0)
            account.verify_type = comprehensive_info['basic_info'].get(
                'verify_type_info', {}).get('id', 0)
            account.username = formatted_info['user_name']
            account.principal_name = formatted_info['principal_name']
            account.alias = formatted_info['alias']
            account.qrcode_url = formatted_info['qrcode_url']
            account.total_revenue = formatted_info['total_revenue']
            account.yesterday_revenue = formatted_info['yesterday_revenue']
            account.draft_count = formatted_info['draft_count']
            account.updated_time = datetime.utcnow()

            success_count += 1
            logger.info(
                f"公众号信息同步成功: ID={account.id}, 昵称={formatted_info['nickname']}, AppID={account.account_appID}")
            results.append({
                'account_id': account.id,
                'nickname': formatted_info['nickname'],
                'status': 'success',
                'data': formatted_info if len(id_list) == 1 else None
            })

        except Exception as e:
            logger.error(
                f"公众号信息同步失败: ID={account.id}, 昵称={account.nickname}, AppID={account.account_appID}, 错误={str(e)}")
            results.append({
                'account_id': account.id,
                'nickname': account.nickname,
                'status': 'error',
                'message': str(e)
            })

    db.session.commit()

    # 根据同步的数量返回不同的响应
    if len(id_list) == 1:
        if results[0]['status'] == 'success':
            return success(results[0]['data'], '公众号信息同步成功')
        else:
            return error(results[0]['message'])
    else:
        return success(results, f'批量同步完成！成功: {success_count}，失败: {len(results) - success_count}')


@public_account_bp.route('/auth/qr_code', methods=['GET'])
@catch_exceptions
@login_required
def get_auth_qr_code():
    """获取授权二维码"""
    try:
        qr_data = wechat_auth.generate_auth_qr_code()

        logger.info(f"授权二维码生成成功: AuthCode={qr_data['auth_code']}")
        return success({
            'auth_code': qr_data['auth_code'],
            'auth_url': qr_data['auth_url'],
            'qr_code': qr_data['qr_code']
        }, '生成二维码成功')
    except Exception as e:
        logger.error(f"授权二维码生成失败: 错误={str(e)}")
        raise ValueError(f'生成二维码失败: {str(e)}')


@public_account_bp.route('/auth/status', methods=['GET'])
@catch_exceptions
@login_required
def check_auth_status():
    """检查授权状态"""
    # 表单验证
    form = validate_form(AuthStatusForm)
    auth_code = form.auth_code.data

    result = wechat_auth.get_auth_status(auth_code)

    if result.get('code') == 200:
        logger.info(f"授权状态检查成功: AuthCode={auth_code}, 状态=已授权")
        return success(result.get('data'), result.get('message'))
    elif result.get('code') == 202:
        logger.debug(f"授权状态检查: AuthCode={auth_code}, 状态=等待用户授权")
        return success(result.get('data'), result.get('message'), 202)
    else:
        logger.warning(
            f"授权状态检查失败: AuthCode={auth_code}, 错误={result.get('message')}")
        return error(result.get('message'), result.get('code', 400))


@public_account_bp.route('/validate', methods=['POST'])
@catch_exceptions
@login_required
def validate_account_credentials():
    """验证账号凭证并获取公众号信息"""
    # 表单验证
    form = validate_form(ValidateCredentialsForm)

    # 验证凭证并获取公众号信息
    result = wechat_auth.validate_account_credentials(
        form.account_appID.data,
        form.appsecret.data
    )

    if result.get('success'):
        logger.info(f"公众号凭证验证成功: AppID={form.account_appID.data}")
        return success(result.get('data'), result.get('message'))
    else:
        logger.warning(
            f"公众号凭证验证失败: AppID={form.account_appID.data}, 错误={result.get('message')}")
        return error(result.get('message'))


@public_account_bp.route('/info', methods=['POST'])
@catch_exceptions
@login_required
def get_account_info():
    """通过AppID和密钥获取公众号详细信息"""
    # 表单验证
    form = validate_form(ValidateCredentialsForm)

    # 创建临时实例获取基本信息
    temp_data_api = WeChatData(form.account_appID.data, form.appsecret.data)

    # 只获取基本信息，避免权限问题
    basic_info = temp_data_api.get_account_basic_info()
    logger.debug(f"获取公众号基本信息成功: AppID={form.account_appID.data}")

    # 尝试获取用户数量（如果权限不足则忽略）
    user_count = {'total_users': 0, 'current_users': 0}
    try:
        user_count = temp_data_api.get_user_count()
    except Exception as e:
        logger.warning(
            f"获取用户数量失败，使用默认值: AppID={form.account_appID.data}, 错误={str(e)}")

    # 尝试获取草稿箱数量（如果权限不足则忽略）
    draft_count = 0
    try:
        draft_count = temp_data_api.get_draft_count()
    except Exception as e:
        logger.warning(
            f"获取草稿箱数量失败，使用默认值: AppID={form.account_appID.data}, 错误={str(e)}")

    # 获取服务类型和认证类型的名称
    def get_service_type_name(service_type_id):
        service_types = {
            0: '订阅号',
            1: '由历史老帐号升级后的订阅号',
            2: '服务号'
        }
        return service_types.get(service_type_id, '未知')

    def get_verify_type_name(verify_type_id):
        verify_types = {
            -1: '未认证',
            0: '微信认证',
            1: '新浪微博认证',
            2: '腾讯微博认证',
            3: '已资质认证通过但还未通过名称认证',
            4: '已资质认证通过、还未通过名称认证，但通过了新浪微博认证',
            5: '已资质认证通过、还未通过名称认证，但通过了腾讯微博认证'
        }
        return verify_types.get(verify_type_id, '未知')

    # 构建返回的公众号信息
    service_type_id = basic_info.get('service_type_info', {}).get('id', 0)
    verify_type_id = basic_info.get('verify_type_info', {}).get('id', -1)

    account_info = {
        'app_id': form.account_appID.data,
        'nickname': basic_info.get('nickname', ''),
        'head_img': basic_info.get('head_img', ''),
        'service_type': service_type_id,
        'service_type_name': get_service_type_name(service_type_id),
        'verify_type': verify_type_id,
        'verify_type_name': get_verify_type_name(verify_type_id),
        'user_name': basic_info.get('user_name', ''),
        'principal_name': basic_info.get('principal_name', ''),
        'alias': basic_info.get('alias', ''),
        'qrcode_url': basic_info.get('qrcode_url', ''),
        'total_users': user_count.get('total_users', 0),
        'draft_count': draft_count,
        'total_revenue': 0.0,  # 默认值，因为需要数据统计权限才能计算
        'yesterday_revenue': 0.0,  # 默认值
        'business_info': {},  # 基本信息API不包含此字段
        'func_info': []  # 基本信息API不包含此字段
    }

    logger.info(
        f"公众号信息获取成功: AppID={form.account_appID.data}, 昵称={account_info['nickname']}")
    return success(account_info, '公众号信息获取成功')


@public_account_bp.route('/draft/test', methods=['POST'])
@catch_exceptions
@login_required
def test_draft_publish():
    """测试草稿发布"""
    # 创建草稿箱API实例
    from app.extensions.wechat import WeChatDraft
    api = WeChatDraft()

    # 获取access_token
    access_token = api.get_access_token()

    # 测试文章内容
    title = f"Web管理后台测试文章 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    content = f"""
    <h1>通过Web管理后台发布的测试文章</h1>
    <p>发布时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>这是通过Web管理后台扫码授权后发布的测试文章。</p>
    <h2>功能特点</h2>
    <ul>
        <li>Web界面管理</li>
        <li>扫码授权</li>
        <li>实时状态显示</li>
        <li>自动草稿发布</li>
    </ul>
    <p>感谢使用微信公众号管理系统！</p>
    """

    logger.info(f"准备发布测试草稿: 标题={title}")

    # 发布到草稿箱
    try:
        result = api.publish_to_draft(
            title, content, access_token=access_token)
        logger.info(f"测试草稿发布成功: MediaID={result['media_id']}, 标题={title}")
        return success(result, f'草稿发布成功！Media ID: {result["media_id"]}')
    except Exception as e:
        logger.error(f"测试草稿发布失败: 标题={title}, 错误={str(e)}")
        raise ValueError(f'草稿发布失败: {str(e)}')


@public_account_bp.route('/access_token', methods=['GET'])
@catch_exceptions
@login_required
def get_access_token():
    """获取微信公众号access_token"""
    try:
        access_token = wechat_data.get_access_token()
        logger.info(
            f"获取access_token成功: Token长度={len(access_token) if access_token else 0}")
        return success({
            'access_token': access_token,
            'expires_in': 7200
        }, '获取access_token成功')
    except Exception as e:
        logger.error(f"获取access_token失败: 错误={str(e)}")
        raise ValueError(f'获取access_token失败: {str(e)}')
