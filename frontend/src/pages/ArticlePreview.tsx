import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Space, message, Tag, Spin, Typography, Divider } from 'antd';
import { ArrowLeftOutlined, CalendarOutlined, UserOutlined, TagOutlined } from '@ant-design/icons';
import { Article } from '../types';
import { articleService } from '../services/articleService';

const { Title, Text } = Typography;

const ArticlePreview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadArticle = async () => {
      if (!id) {
        message.error('文章ID不存在');
        navigate('/articles');
        return;
      }

      try {
        setLoading(true);
        const response = await articleService.getArticleDetail(Number(id));
        if (response.data) {
          setArticle(response.data);
        } else {
          message.error('文章不存在');
          navigate('/articles');
        }
      } catch (error) {
        // 错误已在 api.ts 中统一处理
        navigate('/articles');
      } finally {
        setLoading(false);
      }
    };

    loadArticle();
  }, [id, navigate]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载中...</div>
      </div>
    );
  }

  if (!article) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div>文章不存在</div>
        <Button 
          type="primary" 
          onClick={() => navigate('/articles')}
          style={{ marginTop: 16 }}
        >
          返回文章列表
        </Button>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case '草稿': return 'default';
      case '已发布': return 'success';
      case '发布中': return 'processing';
      case '发布失败': return 'error';
      default: return 'default';
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '20px' }}>
      {/* 头部操作区 */}
      <Card style={{ marginBottom: 20 }}>
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(`/articles/${id}/edit`)}
          >
            返回编辑
          </Button>
          <Button 
            onClick={() => navigate('/articles')}
          >
            文章列表
          </Button>
        </Space>
      </Card>

      {/* 文章预览区 */}
      <Card>
        {/* 文章标题 */}
        <div style={{ textAlign: 'center', marginBottom: 30 }}>
          <Title level={1} style={{ marginBottom: 8 }}>
            {article.title}
          </Title>
          
          {/* 文章元信息 */}
          <Space size="large" style={{ color: '#666' }}>
            {article.author_nickname && (
              <Space size={4}>
                <UserOutlined />
                <Text type="secondary">{article.author_nickname}</Text>
              </Space>
            )}
            
            {article.category && (
              <Space size={4}>
                <TagOutlined />
                <Text type="secondary">{article.category}</Text>
              </Space>
            )}
            
            <Space size={4}>
              <CalendarOutlined />
              <Text type="secondary">{article.created_time}</Text>
            </Space>
            
            <Tag color={getStatusColor(article.status)}>
              {article.status}
            </Tag>
          </Space>
        </div>

        <Divider />

        {/* 文章内容 */}
        <div 
          style={{
            fontSize: 16,
            lineHeight: 1.8,
            color: '#333',
            minHeight: 200,
          }}
          className="article-content"
        >
          <style>
            {`
              .article-content img {
                max-width: 100% !important;
                width: auto !important;
                height: auto !important;
                display: block !important;
                margin: 24px auto !important;
                border-radius: 8px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
              }
              .article-content p {
                margin: 16px 0 !important;
                text-align: justify !important;
              }
              .article-content h1, .article-content h2, .article-content h3,
              .article-content h4, .article-content h5, .article-content h6 {
                margin: 24px 0 16px 0 !important;
                color: #262626 !important;
              }
              .article-content blockquote {
                margin: 16px 0 !important;
                padding: 12px 20px !important;
                background: #f6f8fa !important;
                border-left: 4px solid #1890ff !important;
                border-radius: 4px !important;
              }
              .article-content ul, .article-content ol {
                margin: 16px 0 !important;
                padding-left: 24px !important;
              }
              .article-content li {
                margin: 8px 0 !important;
              }
            `}
          </style>
          <div dangerouslySetInnerHTML={{ __html: article.content_html || '' }} />
        </div>

        {/* 文章统计信息 */}
        <Divider />
        <div style={{ textAlign: 'center', color: '#999', fontSize: 14 }}>
          <Space size="large">
            <span>字数: {article.word_count || 0}</span>
            {article.public_account_nickname && (
              <span>公众号: {article.public_account_nickname}</span>
            )}
            {article.saved_status && (
              <span>存稿状态: {article.saved_status}</span>
            )}
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default ArticlePreview; 