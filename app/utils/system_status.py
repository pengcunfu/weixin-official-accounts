import psutil
import platform
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# CPU 采样间隔（秒）：取值越小接口响应越快
CPU_SAMPLE_INTERVAL = 0.3

# 系统状态缓存有效期（秒）：避免首页多次刷新时重复执行昂贵的系统采样
SYSTEM_STATUS_CACHE_TTL = 10


class SystemMonitor:
    """系统状态监控类"""
    
    def __init__(self):
        self.start_time = datetime.now()
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        try:
            # CPU使用率（短间隔采样，避免阻塞接口响应）
            cpu_percent = psutil.cpu_percent(interval=CPU_SAMPLE_INTERVAL)
            
            # CPU核心数
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # CPU频率
            cpu_freq = psutil.cpu_freq()
            
            return {
                'percent': round(cpu_percent, 1),
                'count': cpu_count,
                'count_logical': cpu_count_logical,
                'frequency': {
                    'current': round(cpu_freq.current, 2) if cpu_freq else None,
                    'min': round(cpu_freq.min, 2) if cpu_freq else None,
                    'max': round(cpu_freq.max, 2) if cpu_freq else None,
                } if cpu_freq else None,
                'status': self._get_status_by_percent(cpu_percent, 70, 90)
            }
        except Exception as e:
            return {
                'percent': 0,
                'error': str(e),
                'status': 'unknown'
            }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        try:
            # 内存信息
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'percent': round(memory.percent, 1),
                'total': self._bytes_to_gb(memory.total),
                'available': self._bytes_to_gb(memory.available),
                'used': self._bytes_to_gb(memory.used),
                'free': self._bytes_to_gb(memory.free),
                'swap': {
                    'total': self._bytes_to_gb(swap.total),
                    'used': self._bytes_to_gb(swap.used),
                    'free': self._bytes_to_gb(swap.free),
                    'percent': round(swap.percent, 1)
                },
                'status': self._get_status_by_percent(memory.percent, 75, 90)
            }
        except Exception as e:
            return {
                'percent': 0,
                'error': str(e),
                'status': 'unknown'
            }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        try:
            # 获取根目录磁盘使用情况
            disk_usage = psutil.disk_usage('/')
            
            # 获取所有磁盘分区
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': self._bytes_to_gb(partition_usage.total),
                        'used': self._bytes_to_gb(partition_usage.used),
                        'free': self._bytes_to_gb(partition_usage.free),
                        'percent': round((partition_usage.used / partition_usage.total) * 100, 1)
                    })
                except PermissionError:
                    # 某些分区可能没有权限访问
                    continue
            
            main_disk_percent = round((disk_usage.used / disk_usage.total) * 100, 1)
            
            return {
                'percent': main_disk_percent,
                'total': self._bytes_to_gb(disk_usage.total),
                'used': self._bytes_to_gb(disk_usage.used),
                'free': self._bytes_to_gb(disk_usage.free),
                'partitions': partitions,
                'status': self._get_status_by_percent(main_disk_percent, 80, 95)
            }
        except Exception as e:
            return {
                'percent': 0,
                'error': str(e),
                'status': 'unknown'
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        try:
            # 网络IO统计
            net_io = psutil.net_io_counters()
            
            # 网络连接数
            connections = len(psutil.net_connections())
            
            return {
                'bytes_sent': self._bytes_to_mb(net_io.bytes_sent),
                'bytes_recv': self._bytes_to_mb(net_io.bytes_recv),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'connections': connections,
                'status': 'normal'
            }
        except Exception as e:
            return {
                'error': str(e),
                'status': 'unknown'
            }
    
    def get_process_info(self) -> Dict[str, Any]:
        """获取进程信息"""
        try:
            # 进程数量
            process_count = len(psutil.pids())
            
            # 获取当前进程信息
            current_process = psutil.Process()
            
            # 获取系统负载（仅限Unix系统）
            load_avg = None
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                # Windows系统不支持
                pass
            
            return {
                'count': process_count,
                'current_process': {
                    'pid': current_process.pid,
                    'memory_percent': round(current_process.memory_percent(), 2),
                    'cpu_percent': round(current_process.cpu_percent(), 2)
                },
                'load_average': load_avg,
                'status': 'normal'
            }
        except Exception as e:
            return {
                'error': str(e),
                'status': 'unknown'
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统基本信息"""
        try:
            # 系统信息
            uname = platform.uname()
            
            # 系统启动时间
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'system': uname.system,
                'node': uname.node,
                'release': uname.release,
                'version': uname.version,
                'machine': uname.machine,
                'processor': uname.processor,
                'boot_time': boot_time.isoformat(),
                'uptime_seconds': int(uptime.total_seconds()),
                'uptime_string': self._format_uptime(uptime),
                'python_version': platform.python_version()
            }
        except Exception as e:
            return {
                'error': str(e),
                'system': 'unknown'
            }
    
    def get_overall_health(
        self,
        cpu_info: Optional[Dict[str, Any]] = None,
        memory_info: Optional[Dict[str, Any]] = None,
        disk_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """获取系统整体健康状况"""
        try:
            if cpu_info is None:
                cpu_info = self.get_cpu_info()
            if memory_info is None:
                memory_info = self.get_memory_info()
            if disk_info is None:
                disk_info = self.get_disk_info()
            
            # 计算健康分数
            health_score = 100
            issues = []
            
            # CPU检查
            if cpu_info['percent'] > 90:
                health_score -= 20
                issues.append('CPU使用率过高')
            elif cpu_info['percent'] > 70:
                health_score -= 10
                issues.append('CPU使用率较高')
            
            # 内存检查
            if memory_info['percent'] > 90:
                health_score -= 25
                issues.append('内存使用率过高')
            elif memory_info['percent'] > 75:
                health_score -= 15
                issues.append('内存使用率较高')
            
            # 磁盘检查
            if disk_info['percent'] > 95:
                health_score -= 30
                issues.append('磁盘空间严重不足')
            elif disk_info['percent'] > 80:
                health_score -= 10
                issues.append('磁盘空间不足')
            
            # 确定健康状态
            if health_score >= 90:
                status = 'excellent'
                status_text = '系统运行正常，所有服务可用'
                status_color = 'success'
            elif health_score >= 75:
                status = 'good'
                status_text = '系统运行良好，有轻微问题'
                status_color = 'success'
            elif health_score >= 60:
                status = 'warning'
                status_text = '系统有一些性能问题，需要关注'
                status_color = 'warning'
            else:
                status = 'critical'
                status_text = '系统存在严重问题，需要立即处理'
                status_color = 'error'
            
            return {
                'score': max(0, health_score),
                'status': status,
                'message': status_text,
                'color': status_color,
                'issues': issues,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'score': 0,
                'status': 'unknown',
                'message': f'无法获取系统健康状况: {str(e)}',
                'color': 'error',
                'issues': ['系统监控异常'],
                'timestamp': datetime.now().isoformat()
            }
    
    def get_complete_status(self) -> Dict[str, Any]:
        """获取完整的系统状态信息"""
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        disk_info = self.get_disk_info()
        return {
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'network': self.get_network_info(),
            'process': self.get_process_info(),
            'system': self.get_system_info(),
            'health': self.get_overall_health(
                cpu_info=cpu_info,
                memory_info=memory_info,
                disk_info=disk_info,
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _bytes_to_gb(self, bytes_value: int) -> float:
        """字节转换为GB"""
        return round(bytes_value / (1024 ** 3), 2)
    
    def _bytes_to_mb(self, bytes_value: int) -> float:
        """字节转换为MB"""
        return round(bytes_value / (1024 ** 2), 2)
    
    def _get_status_by_percent(self, percent: float, warning_threshold: float, critical_threshold: float) -> str:
        """根据百分比获取状态"""
        if percent >= critical_threshold:
            return 'critical'
        elif percent >= warning_threshold:
            return 'warning'
        else:
            return 'normal'
    
    def _format_uptime(self, uptime: timedelta) -> str:
        """格式化运行时间"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天 {hours}小时 {minutes}分钟"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"


# 全局系统监控实例
system_monitor = SystemMonitor()

# 系统状态缓存：{timestamp: 最后生成时间, data: 缓存数据}
_system_status_cache = {
    'timestamp': 0.0,
    'data': None,
}


def get_system_status() -> Dict[str, Any]:
    """获取系统状态（简化版，用于Dashboard）"""
    try:
        now = time.monotonic()
        cached = _system_status_cache['data']
        if cached is not None and now - _system_status_cache['timestamp'] < SYSTEM_STATUS_CACHE_TTL:
            return cached

        # 只采样一次，避免 CPU/内存/磁盘被重复读取
        cpu_info = system_monitor.get_cpu_info()
        memory_info = system_monitor.get_memory_info()
        disk_info = system_monitor.get_disk_info()
        health_info = system_monitor.get_overall_health(
            cpu_info=cpu_info,
            memory_info=memory_info,
            disk_info=disk_info,
        )

        status = {
            'server_status': {
                'percent': health_info['score'],
                'status': '正常' if health_info['status'] in ['excellent', 'good'] else '异常',
                'color': health_info['color']
            },
            'memory_usage': {
                'percent': memory_info['percent'],
                'status': memory_info['status'],
                'used_gb': memory_info['used'],
                'total_gb': memory_info['total']
            },
            'cpu_usage': {
                'percent': cpu_info['percent'],
                'status': cpu_info['status'],
                'count': cpu_info.get('count', 0)
            },
            'disk_space': {
                'percent': disk_info['percent'],
                'status': disk_info['status'],
                'used_gb': disk_info['used'],
                'total_gb': disk_info['total']
            },
            'overall_status': {
                'message': health_info['message'],
                'type': health_info['color'],
                'issues': health_info['issues']
            }
        }

        _system_status_cache['timestamp'] = now
        _system_status_cache['data'] = status
        return status
    except Exception as e:
        return {
            'server_status': {
                'percent': 0,
                'status': '无法获取',
                'color': 'error'
            },
            'memory_usage': {
                'percent': 0,
                'status': 'unknown'
            },
            'cpu_usage': {
                'percent': 0,
                'status': 'unknown'
            },
            'disk_space': {
                'percent': 0,
                'status': 'unknown'
            },
            'overall_status': {
                'message': f'系统监控服务异常: {str(e)}',
                'type': 'error',
                'issues': ['监控服务不可用']
            }
        }


def get_detailed_system_info() -> Dict[str, Any]:
    """获取详细的系统信息"""
    return system_monitor.get_complete_status()


def check_system_health() -> bool:
    """检查系统健康状况"""
    try:
        health_info = system_monitor.get_overall_health()
        return health_info['status'] in ['excellent', 'good']
    except Exception:
        return False
