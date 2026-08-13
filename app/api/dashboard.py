from flask import Blueprint, jsonify, request
from app.decorator.auth import login_required
from app.utils.json_result import success, error
from app.utils.system_status import get_system_status as get_real_system_status, get_detailed_system_info, \
    check_system_health
from datetime import datetime, timedelta
import random

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """获取Dashboard主要统计数据"""
    try:
        # 这里后续可以从数据库获取真实数据
        stats = {
            'username': 'admin',
            'isMainAccount': True,
            'authorizedAccounts': 15,
            'totalAccounts': 15,
            'loginCount': 18,
            'childAccountCount': 0,
            'accountRevenue': 3439.3,
            'dailyAccountRevenue': 0.2
        }
        return success(data=stats)
    except Exception as e:
        return error(message=f"获取统计数据失败: {str(e)}")


@dashboard_bp.route('/revenue-chart', methods=['GET'])
@login_required
def get_revenue_chart():
    """获取总收益图表数据"""
    try:
        revenue_data = [
            {'name': '朋友圈主题', 'value': 0},
            {'name': '朋友圈故事', 'value': 0},
            {'name': '朋友圈问答', 'value': 0},
            {'name': '人员简历平台', 'value': 0},
            {'name': '朋友圈客服', 'value': 0},
            {'name': '快递管家', 'value': 1800},
            {'name': '快递之家', 'value': 200},
            {'name': '朋友圈故事2', 'value': 0},
            {'name': '朋友圈平台', 'value': 800}
        ]
        return success(data=revenue_data)
    except Exception as e:
        return error(message=f"获取收益图表数据失败: {str(e)}")


@dashboard_bp.route('/daily-revenue-chart', methods=['GET'])
@login_required
def get_daily_revenue_chart():
    """获取日收益趋势图表数据"""
    try:
        # 生成最近7天的数据
        daily_revenue_data = []
        base_date = datetime.now() - timedelta(days=6)

        for i in range(7):
            current_date = base_date + timedelta(days=i)
            daily_revenue_data.append({
                'name': current_date.strftime('%Y-%m-%d'),
                'value': round(random.uniform(0.1, 1.5), 1),
                'revenue': round(random.uniform(0.1, 1.5), 1)
            })

        return success(data=daily_revenue_data)
    except Exception as e:
        return error(message=f"获取日收益图表数据失败: {str(e)}")


@dashboard_bp.route('/activities', methods=['GET'])
@login_required
def get_recent_activities():
    """获取最近活动数据"""
    try:
        activities = [
            {
                'id': '1',
                'type': 'article',
                'title': '发布了新文章《微信小程序开发指南》',
                'time': '10分钟前',
                'status': 'success'
            },
            {
                'id': '2',
                'type': 'account',
                'title': '添加了新的公众号《技术分享》',
                'time': '1小时前',
                'status': 'info'
            },
            {
                'id': '3',
                'type': 'revenue',
                'title': '快递管家账号收益 +1.2元',
                'time': '2小时前',
                'status': 'success'
            },
            {
                'id': '4',
                'type': 'user',
                'title': '子账号登录系统',
                'time': '3小时前',
                'status': 'info'
            },
            {
                'id': '5',
                'type': 'article',
                'title': '文章《React最佳实践》发布成功',
                'time': '4小时前',
                'status': 'success'
            },
            {
                'id': '6',
                'type': 'revenue',
                'title': '朋友圈平台账号收益 +0.8元',
                'time': '5小时前',
                'status': 'success'
            },
            {
                'id': '7',
                'type': 'account',
                'title': '公众号《生活助手》授权更新',
                'time': '6小时前',
                'status': 'warning'
            }
        ]
        return success(data=activities)
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
    """获取详细统计数据"""
    try:
        detailed_stats = {
            'weekly_articles': {
                'value': 12,
                'suffix': '篇',
                'trend': {
                    'type': 'increase',
                    'percent': 20,
                    'text': '比上周增长 20%'
                }
            },
            'monthly_views': {
                'value': 25680,
                'suffix': '次',
                'trend': {
                    'type': 'increase',
                    'percent': 15,
                    'text': '比上月增长 15%'
                }
            },
            'active_accounts': {
                'value': 8,
                'suffix': '个',
                'total': 15,
                'text': '总共 15 个公众号'
            },
            'daily_revenue': {
                'value': 0.2,
                'suffix': '元',
                'precision': 1,
                'trend': {
                    'type': 'stable',
                    'text': '收益稳定增长'
                }
            }
        }
        return success(data=detailed_stats)
    except Exception as e:
        return error(message=f"获取详细统计数据失败: {str(e)}")
