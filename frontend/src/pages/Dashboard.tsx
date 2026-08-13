import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Spin, Button, List, Typography, Progress, Tag, Empty } from 'antd';
import {
  FileTextOutlined,
  TeamOutlined,
  UserOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  UploadOutlined,
  EyeOutlined,
  RiseOutlined,
  DollarOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { 
  dashboardService, 
  DashboardStats, 
  ChartData, 
  ActivityItem, 
  SystemStatus, 
  DetailedStats 
} from '../services/dashboardService';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const { Title, Paragraph, Text } = Typography;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    username: 'admin',
    isMainAccount: true,
    authorizedAccounts: 15,
    totalAccounts: 15,
    loginCount: 18,
    childAccountCount: 0,
    accountRevenue: 3439.3,
    dailyAccountRevenue: 0.2
  });
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [revenueChartData, setRevenueChartData] = useState<ChartData[]>([]);
  const [dailyRevenueChartData, setDailyRevenueChartData] = useState<ChartData[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [detailedStats, setDetailedStats] = useState<DetailedStats | null>(null);
  const [loading, setLoading] = useState(true);



  const categoryColors = [
    '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
    '#82CA9D', '#FFC658', '#8DD1E1', '#D084D0', '#FFABAB'
  ];

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        
        // 并行加载所有数据
        const [
          statsResponse,
          revenueChartResponse,
          dailyRevenueChartResponse,
          activitiesResponse,
          systemStatusResponse,
          detailedStatsResponse
        ] = await Promise.all([
          dashboardService.getDashboardStats(),
          dashboardService.getRevenueChart(),
          dashboardService.getDailyRevenueChart(),
          dashboardService.getRecentActivities(),
          dashboardService.getSystemStatus(),
          dashboardService.getDetailedStats()
        ]);

        // 更新状态
        if (statsResponse.data) {
          setStats(statsResponse.data);
        }
        
        if (revenueChartResponse.data) {
          setRevenueChartData(revenueChartResponse.data);
        }
        
        if (dailyRevenueChartResponse.data) {
          setDailyRevenueChartData(dailyRevenueChartResponse.data);
        }
        
        if (activitiesResponse.data) {
          setActivities(activitiesResponse.data);
        }
        
        if (systemStatusResponse.data) {
          setSystemStatus(systemStatusResponse.data);
        }
        
        if (detailedStatsResponse.data) {
          setDetailedStats(detailedStatsResponse.data);
        }
        
      } catch (error) {
        // 错误已在 api.ts 中统一处理
        console.error('加载Dashboard数据失败:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getActivityIcon = (type: string) => {
    const iconStyle = { marginRight: 12, color: '#1890ff' };
    switch (type) {
      case 'article':
        return <FileTextOutlined style={iconStyle} />;
      case 'account':
        return <TeamOutlined style={iconStyle} />;
      case 'user':
        return <UserOutlined style={iconStyle} />;
      case 'revenue':
        return <DollarOutlined style={iconStyle} />;
      default:
        return <ClockCircleOutlined style={iconStyle} />;
    }
  };

  return (
    <div>
      {/* 欢迎区域 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>欢迎回来</Title>
        <Paragraph type="secondary">
          登录账号：{stats.username} | 主账号 | 已授权账号：{stats.authorizedAccounts}个
        </Paragraph>
      </div>

      {/* 核心统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
             <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>{stats.username}</div>
             <div style={{ color: '#666', marginTop: 8 }}>登录账号</div>
            </div>
           </Card>
        </Col>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>主账号</div>
            <div style={{ color: '#666', marginTop: 8 }}>是否主账号</div>
            </div>
          </Card>
        </Col>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>{stats.authorizedAccounts}</div>
            <div style={{ color: '#666', marginTop: 8 }}>已授权账号(个)</div>
            </div>
          </Card>
        </Col>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>{stats.totalAccounts}</div>
            <div style={{ color: '#666', marginTop: 8 }}>累计账号总数</div>
            </div>
          </Card>
        </Col>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#fa8c16' }}>{stats.loginCount}</div>
            <div style={{ color: '#666', marginTop: 8 }}>登录次数</div>
            </div>
          </Card>
        </Col>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#eb2f96' }}>{stats.childAccountCount}</div>
            <div style={{ color: '#666', marginTop: 8 }}>子账号个数</div>
            </div>
          </Card>
        </Col>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#13c2c2' }}>{stats.accountRevenue}</div>
            <div style={{ color: '#666', marginTop: 8 }}>账号累计总收益</div>
            </div>
          </Card>
        </Col>
        <Col span={3}>
          <Card loading={loading} style={{ textAlign: 'center', height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>{stats.dailyAccountRevenue}</div>
            <div style={{ color: '#666', marginTop: 8 }}>昨日账号累计收益</div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 详细统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {detailedStats ? (
          <>
            <Col span={6}>
              <Card>
                <Statistic
                  title="本周发布文章"
                  value={detailedStats.weekly_articles.value}
                  prefix={<TrophyOutlined style={{ color: '#1890ff' }} />}
                  suffix={detailedStats.weekly_articles.suffix}
                  valueStyle={{ color: '#1890ff' }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text type={detailedStats.weekly_articles.trend.type === 'increase' ? 'success' : 'secondary'}>
                    {detailedStats.weekly_articles.trend.type === 'increase' ? <RiseOutlined /> : null} {detailedStats.weekly_articles.trend.text}
                  </Text>
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="本月总阅读量"
                  value={detailedStats.monthly_views.value}
                  prefix={<EyeOutlined style={{ color: '#52c41a' }} />}
                  suffix={detailedStats.monthly_views.suffix}
                  valueStyle={{ color: '#52c41a' }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text type={detailedStats.monthly_views.trend.type === 'increase' ? 'success' : 'secondary'}>
                    {detailedStats.monthly_views.trend.type === 'increase' ? <RiseOutlined /> : null} {detailedStats.monthly_views.trend.text}
                  </Text>
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="活跃公众号"
                  value={detailedStats.active_accounts.value}
                  prefix={<TeamOutlined style={{ color: '#fa8c16' }} />}
                  suffix={detailedStats.active_accounts.suffix}
                  valueStyle={{ color: '#fa8c16' }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary">
                    {detailedStats.active_accounts.text}
                  </Text>
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="今日收益"
                  value={detailedStats.daily_revenue.value}
                  prefix={<DollarOutlined style={{ color: '#eb2f96' }} />}
                  suffix={detailedStats.daily_revenue.suffix}
                  precision={detailedStats.daily_revenue.precision}
                  valueStyle={{ color: '#eb2f96' }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text type="success">
                    <RiseOutlined /> {detailedStats.daily_revenue.trend.text}
                  </Text>
                </div>
              </Card>
            </Col>
          </>
        ) : (
          <Col span={24}>
            <div style={{ textAlign: 'center', padding: 20 }}>
              {loading ? <Spin /> : <Empty description="暂无数据" />}
            </div>
          </Col>
        )}
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* 总收益趋势图 */}
        <Col span={12}>
          <Card title="总收益趋势">
            {revenueChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenueChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#1890ff" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {loading ? <Spin /> : <Empty description="暂无数据" />}
              </div>
            )}
          </Card>
        </Col>

        {/* 日收益趋势 */}
        <Col span={12}>
          <Card title="日收益趋势(多账号的每日累计收入)">
            {dailyRevenueChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyRevenueChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#1890ff" 
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {loading ? <Spin /> : <Empty description="暂无数据" />}
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 操作和活动区域 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* 快速操作 */}
        <Col span={8}>
          <Card title="快速操作">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                block
                onClick={() => navigate('/articles/edit')}
              >
                创建文章
              </Button>
              <Button 
                icon={<UploadOutlined />}
                block
                onClick={() => navigate('/articles/upload')}
              >
                上传文档
              </Button>
              <Button 
                icon={<TeamOutlined />}
                block
                onClick={() => navigate('/accounts')}
              >
                管理公众号
              </Button>
              <Button 
                icon={<EyeOutlined />}
                block
                onClick={() => navigate('/articles')}
              >
                查看文章
              </Button>
              <Button 
                icon={<UserOutlined />}
                block
                onClick={() => navigate('/users')}
              >
                用户管理
              </Button>
            </div>
          </Card>
        </Col>

        {/* 最近活动 */}
        <Col span={8}>
          <Card title="最近活动">
            {activities.length > 0 ? (
              <List
                style={{ maxHeight: 350, overflowY: 'auto' }}
                dataSource={activities}
                renderItem={(item) => (
                  <List.Item style={{ borderBottom: '1px solid #f0f0f0', padding: '12px 0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      {getActivityIcon(item.type)}
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 500, marginBottom: 4 }}>{item.title}</div>
                        <div style={{ color: '#999', fontSize: 12 }}>{item.time}</div>
                      </div>
                      <Tag color={item.status === 'success' ? 'green' : item.status === 'warning' ? 'orange' : 'blue'}>
                        {item.status === 'success' ? '成功' : item.status === 'warning' ? '警告' : '信息'}
                      </Tag>
                    </div>
                  </List.Item>
                )}
              />
            ) : (
              <div style={{ height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {loading ? <Spin /> : <Empty description="暂无活动" />}
              </div>
            )}
          </Card>
        </Col>

        {/* 系统状态 */}
        <Col span={8}>
          <Card title="系统状态">
            {systemStatus ? (
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>
                <Text>服务器状态</Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: 4 }}>
                    <Progress percent={systemStatus.server_status.percent} status="active" showInfo={false} />
                    <span style={{ marginLeft: 8, color: '#52c41a', whiteSpace: 'nowrap' }}>{systemStatus.server_status.status}</span>
                </div>
              </div>
              
              <div style={{ marginBottom: 8 }}>
                <Text>内存使用</Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: 4 }}>
                    <Progress percent={systemStatus.memory_usage.percent} showInfo={false} />
                    <span style={{ marginLeft: 8, whiteSpace: 'nowrap' }}>{systemStatus.memory_usage.percent}%</span>
                </div>
              </div>
              
              <div style={{ marginBottom: 8 }}>
                <Text>CPU使用率</Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: 4 }}>
                    <Progress percent={systemStatus.cpu_usage.percent} showInfo={false} />
                    <span style={{ marginLeft: 8, whiteSpace: 'nowrap' }}>{systemStatus.cpu_usage.percent}%</span>
                </div>
              </div>
              
              <div style={{ marginBottom: 16 }}>
                <Text>磁盘空间</Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: 4 }}>
                    <Progress percent={systemStatus.disk_space.percent} showInfo={false} />
                    <span style={{ marginLeft: 8, whiteSpace: 'nowrap' }}>{systemStatus.disk_space.percent}%</span>
                </div>
              </div>

              <div style={{ padding: 12, background: '#f6ffed', borderRadius: 6, border: '1px solid #b7eb8f' }}>
                <Text style={{ fontSize: 12, color: '#389e0d' }}>
                  <ClockCircleOutlined style={{ marginRight: 4 }} />
                    {systemStatus.overall_status.message}
                </Text>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 20 }}>
                {loading ? <Spin /> : <Empty description="暂无状态" />}
              </div>
            )}
          </Card>
        </Col>
      </Row>


    </div>
  );
};

export default Dashboard; 
