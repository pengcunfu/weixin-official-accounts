from flask import Blueprint, g
from app.decorator.auth import login_required
from app.utils.json_result import success, error
from app.utils.system_status import get_system_status as get_real_system_status, get_detailed_system_info, \
    check_system_health
from app.models.public_account import PublicAccount
from app.models.article import Article
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

ACTIVE_ARTICLE_STATUS = ['已发布', '发布中', '待发布']


def _to_rel_time(dt: datetime) -> str:
    """将时间转换为相对时间描述"""
    now = datetime.now()
    delta = now - dt
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 60:
        return '刚刚'
    minutes = seconds // 60
    if minutes < 60:
        return f'{minutes}分钟前'
    hours = minutes // 60
    if hours < 24:
        return f'{hours}小时前'
    days = hours // 24
    if days < 30:
        return f'{days}天前'
    return dt.strftime('%Y-%m-%d')


def _sum_revenue(column) -> float:
    """安全地求和收益字段（处理 Numeric 与 None）"""
    result = PublicAccount.query.with_entities(
        func.coalesce(func.sum(column), 0)).scalar()
    return float(result or 0)


@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """获取Dashboard主要统计数据（从数据库真实统计）"""
    try:
        user = getattr(g, 'user', None)

        account_active = PublicAccount.get_active()
        user_active = User.get_active()
        article_active = Article.get_active()

        total_accounts = account_active.count()
        authorized_accounts = account_active.filter_by(authorized=True).count()
        child_account_count = user_active.filter_by(is_main=False).count()
        article_count = article_active.count()
        published_article_count = article_active.filter(
            Article.status.in_(ACTIVE_ARTICLE_STATUS)).count()

        stats = {
            # 当前登录用户
            'username': user.username if user else '',
            'isMainAccount': bool(user.is_main) if user else False,
            'loginCount': user.login_count if user else 0,
            # 公众号
            'authorizedAccounts': authorized_accounts,
            'totalAccounts': total_accounts,
            'childAccountCount': child_account_count,
            # 文章
            'articleCount': article_count,
            'publishedArticleCount': published_article_count,
            # 收益（来自公众号累计/昨日收益）
            'totalRevenue': _sum_revenue(PublicAccount.total_revenue),
            'yesterdayRevenue': _sum_revenue(PublicAccount.yesterday_revenue),
        }
        return success(data=stats)
    except Exception as e:
        return error(message=f"获取统计数据失败: {str(e)}")


@dashboard_bp.route('/revenue-chart', methods=['GET'])
@login_required
def get_revenue_chart():
    """获取总收益分布（各已授权公众号累计收益，真实数据）"""
    try:
        accounts = PublicAccount.get_active().filter(
            PublicAccount.authorized == True).all()
        revenue_data = [
            {'name': a.nickname or a.account_appID, 'value': float(a.total_revenue or 0)}
            for a in accounts if (a.total_revenue or 0) > 0
        ]
        return success(data=revenue_data)
    except Exception as e:
        return error(message=f"获取收益图表数据失败: {str(e)}")


@dashboard_bp.route('/daily-revenue-chart', methods=['GET'])
@login_required
def get_daily_revenue_chart():
    """获取昨日收益对比（各已授权公众号昨日收益，真实数据）"""
    try:
        accounts = PublicAccount.get_active().filter(
            PublicAccount.authorized == True).all()
        daily_revenue_data = [
            {'name': a.nickname or a.account_appID,
             'value': float(a.yesterday_revenue or 0),
             'revenue': float(a.yesterday_revenue or 0)}
            for a in accounts if (a.yesterday_revenue or 0) > 0
        ]
        return success(data=daily_revenue_data)
    except Exception as e:
        return error(message=f"获取昨日收益图表数据失败: {str(e)}")


@dashboard_bp.route('/activities', methods=['GET'])
@login_required
def get_recent_activities():
    """获取最近活动（基于文章与公众号的真实创建记录）"""
    try:
        activities = []

        # 最近创建的文章
        articles = Article.get_active().order_by(
            Article.created_time.desc()).limit(6).all()
        for a in articles:
            status_label = '发布' if a.status == '已发布' else '上传'
            activities.append({
                'id': f'article-{a.id}',
                'type': 'article',
                'title': f'{status_label}了文章《{a.title}》',
                'time': _to_rel_time(a.created_time) if a.created_time else '',
                'status': 'success' if a.status == '已发布' else 'info',
                'sort_time': a.created_time.isoformat() if a.created_time else '0000',
            })

        # 最近创建的公众号
        accounts = PublicAccount.get_active().order_by(
            PublicAccount.created_time.desc()).limit(5).all()
        for acc in accounts:
            activities.append({
                'id': f'account-{acc.id}',
                'type': 'account',
                'title': f"新增公众号《{acc.nickname or acc.account_appID}》",
                'time': _to_rel_time(acc.created_time) if acc.created_time else '',
                'status': 'success' if acc.authorized else 'info',
                'sort_time': acc.created_time.isoformat() if acc.created_time else '0000',
            })

        # 按真实时间倒序，取前10
        activities.sort(key=lambda x: x['sort_time'], reverse=True)
        return success(data=activities[:10])
    except Exception as e:
        return error(message=f"获取最近活动失败: {str(e)}")


@dashboard_bp.route('/system-status', methods=['GET'])
@login_required
def get_system_status():
    """获取系统状态数据"""
    system_status = get_real_system_status()
    return success(data=system_status)


@dashboard_bp.route('/system-info', methods=['GET'])
@login_required
def get_detailed_system_info():
    """获取详细的系统信息"""
    try:
        detailed_info = get_detailed_system_info()
        return success(data=detailed_info)
    except Exception as e:
        return error(message=f"获取详细系统信息失败: {str(e)}")


@dashboard_bp.route('/system-health', methods=['GET'])
@login_required
def check_system_health_status():
    """检查系统健康状况"""
    try:
        is_healthy = check_system_health()
        health_status = {
            'healthy': is_healthy,
            'status': 'healthy' if is_healthy else 'unhealthy',
            'message': '系统运行正常' if is_healthy else '系统存在性能问题',
            'timestamp': datetime.now().isoformat()
        }
        return success(data=health_status)
    except Exception as e:
        return error(message=f"检查系统健康状况失败: {str(e)}")


@dashboard_bp.route('/detailed-stats', methods=['GET'])
@login_required
def get_detailed_stats():
    """获取详细统计数据（仅返回可真实计算的项）"""
    try:
        accounts = PublicAccount.get_active()
        total_accounts = accounts.count()
        active_accounts = accounts.filter_by(authorized=True).count()

        # 本周已发布文章数
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        weekly_published = Article.get_active().filter(
            Article.status == '已发布',
            Article.created_time >= week_start
        ).count()
        weekly_total = Article.get_active().count()

        detailed_stats = {
            'weekly_articles': {
                'value': weekly_published,
                'suffix': '篇',
                'trend': {
                    'type': 'stable',
                    'text': f'本周发布，共 {weekly_total} 篇文章'
                }
            },
            'active_accounts': {
                'value': active_accounts,
                'suffix': '个',
                'total': total_accounts,
                'text': f'共 {total_accounts} 个公众号'
            },
            'daily_revenue': {
                'value': _sum_revenue(PublicAccount.yesterday_revenue),
                'suffix': '元',
                'precision': 2,
                'trend': {
                    'type': 'stable',
                    'text': '昨日收益'
                }
            }
        }
        return success(data=detailed_stats)
    except Exception as e:
        return error(message=f"获取详细统计数据失败: {str(e)}")