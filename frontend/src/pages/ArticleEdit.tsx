import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Form, Input, Select, Button, Space, message, Row, Col, Image, Tag, Modal, Typography, Divider } from 'antd';
import { SaveOutlined, ArrowLeftOutlined, EyeOutlined, SendOutlined, CalendarOutlined, UserOutlined, TagOutlined } from '@ant-design/icons';
import { Article, ImageInfo } from '../types';
import { articleService } from '../services/articleService';

const { Option } = Select;
const { Title, Text } = Typography;

const ArticleEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [form] = Form.useForm();
  const editorRef = useRef<any>(null);

  const loadArticle = useCallback(async () => {
    setLoading(true);
    try {
      const response = await articleService.getArticleDetail(Number(id));
      const articleData = response.data;
      if (articleData) {
        setArticle(articleData);
        form.setFieldsValue(articleData);
        
        // 如果有编辑器，设置内容
        if (editorRef.current && articleData.content_html) {
          editorRef.current.innerHTML = articleData.content_html;
        }
      }
    } catch (error) {
      // 错误已在 api.ts 中统一处理
      navigate('/articles');
    } finally {
      setLoading(false);
    }
  }, [id, form, navigate]);

  useEffect(() => {
    if (id) {
      loadArticle();
    }
  }, [id, loadArticle]);

  const handleSave = async (values: any) => {
    setSaving(true);
    try {
      // 获取编辑器内容
      const content_html = editorRef.current?.innerHTML || '';
      
      const submitData = {
        ...values,
        content_html,
      };

      await articleService.updateArticle(Number(id), submitData);
      message.success('保存成功');
      loadArticle(); // 重新加载文章数据
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    try {
      await articleService.publishArticle(Number(id));
      message.success('发布成功');
      loadArticle();
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    }
  };

  const handleSaveToWechat = async () => {
    try {
      await articleService.saveToAccount(Number(id));
      message.success('保存到微信公众号成功');
      loadArticle();
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    }
  };

  const handlePreview = () => {
    setPreviewVisible(true);
  };

  const getPreviewContent = () => {
    const currentContent = editorRef.current?.innerHTML || article?.content_html || '';
    const currentTitle = form.getFieldValue('title') || article?.title || '';
    const currentAuthor = form.getFieldValue('author_nickname') || article?.author_nickname || '';
    const currentCategory = form.getFieldValue('category') || article?.category || '';
    
    return {
      title: currentTitle,
      author: currentAuthor,
      category: currentCategory,
      content: currentContent,
      created_time: article?.created_time || '',
    };
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  if (!article) {
    return <div>文章不存在</div>;
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

  const getStatusText = (status: string) => {
    return status || '草稿';
  };

  const parseImagesInfo = (): ImageInfo[] => {
    try {
      return article.images_info ? JSON.parse(article.images_info) : [];
    } catch {
      return [];
    }
  };

  const imagesInfo = parseImagesInfo();

  return (
    <div>
      <Card
        title={
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/articles')}
            >
              返回
            </Button>
            <span>编辑文章</span>
            <Tag color={getStatusColor(article.status)}>
              {getStatusText(article.status)}
            </Tag>
          </Space>
        }
        extra={
          <Space>
            <Button 
              icon={<EyeOutlined />}
              onClick={handlePreview}
            >
              预览
            </Button>
            <Button 
              type="primary"
              icon={<SaveOutlined />}
              loading={saving}
              onClick={() => form.submit()}
            >
              保存
            </Button>
            <Button 
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSaveToWechat}
              style={{ background: '#52c41a', borderColor: '#52c41a' }}
            >
              保存到微信
            </Button>
          </Space>
        }
      >
        <Row gutter={24}>
          {/* 主编辑区域 */}
          <Col xs={24} lg={16}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
            >
              <Form.Item
                name="title"
                label="标题"
                rules={[{ required: true, message: '请输入文章标题' }]}
              >
                <Input placeholder="请输入文章标题" size="large" />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="category"
                    label="分类"
                    rules={[{ required: true, message: '请选择文章分类' }]}
                  >
                    <Select placeholder="请选择分类">
                      <Option value="科技">科技</Option>
                      <Option value="生活">生活</Option>
                      <Option value="教育">教育</Option>
                      <Option value="娱乐">娱乐</Option>
                      <Option value="其他">其他</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="author_nickname"
                    label="作者"
                  >
                    <Input placeholder="请输入作者名称" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="内容">
                <div>
                  <style>
                    {`
                      .content-editor img {
                        max-width: 100% !important;
                        width: auto !important;
                        height: auto !important;
                        display: block !important;
                        margin: 16px auto !important;
                        border-radius: 6px !important;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
                      }
                      .content-editor p {
                        margin: 12px 0 !important;
                      }
                      .content-editor:focus {
                        outline: none !important;
                        border-color: #40a9ff !important;
                        box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2) !important;
                      }
                    `}
                  </style>
                  <div
                    ref={editorRef}
                    className="content-editor"
                    style={{
                      minHeight: 400,
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                      padding: 16,
                      backgroundColor: '#fff',
                      fontSize: 14,
                      lineHeight: 1.6,
                    }}
                    contentEditable
                    suppressContentEditableWarning
                    dangerouslySetInnerHTML={{ __html: article.content_html || '' }}
                  />
                </div>
                <div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
                  支持富文本编辑，可直接编辑内容、图片等元素
                </div>
              </Form.Item>
            </Form>
          </Col>

          {/* 侧边栏 */}
          <Col xs={24} lg={8}>
            {/* 文章信息 */}
            <Card title="文章信息" size="small" style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8 }}>
                <strong>文件类型:</strong> {article.file_type?.toUpperCase()}
              </div>
              <div style={{ marginBottom: 8 }}>
                <strong>字数:</strong> {article.word_count || 0} 字
              </div>
              <div style={{ marginBottom: 8 }}>
                <strong>创建时间:</strong> {article.created_time}
              </div>
              <div style={{ marginBottom: 8 }}>
                <strong>公众号:</strong> {article.public_account_nickname || '未绑定'}
              </div>
              <div style={{ marginBottom: 8 }}>
                <strong>保存状态:</strong>
                <Tag color={article.saved_status === '已存稿' ? 'success' : 'default'} style={{ marginLeft: 8 }}>
                  {article.saved_status || '未存稿'}
                </Tag>
              </div>
            </Card>

            {/* 图片信息 */}
            {imagesInfo.length > 0 && (
              <Card title={`图片 (${imagesInfo.length})`} size="small" style={{ marginBottom: 16 }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
                  {imagesInfo.map((img: ImageInfo, index: number) => (
                    <div key={index} style={{ position: 'relative' }}>
                      <div style={{ 
                        width: '100%', 
                        aspectRatio: '4/3',
                        overflow: 'hidden',
                        borderRadius: 6,
                        border: '1px solid #f0f0f0',
                        backgroundColor: '#fafafa'
                      }}>
                        <Image
                          src={img.url}
                          alt={img.filename || `图片${index + 1}`}
                          style={{ 
                            width: '100%', 
                            height: '100%',
                            objectFit: 'cover'
                          }}
                          preview={{
                            mask: <EyeOutlined />,
                          }}
                        />
                      </div>
                      <div 
                        style={{ 
                          fontSize: 10, 
                          color: '#666', 
                          marginTop: 6,
                          textAlign: 'center',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          padding: '0 4px'
                        }}
                        title={img.filename}
                      >
                        {img.filename}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* 快捷操作 */}
            <Card title="快捷操作" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button 
                  block
                  onClick={handlePublish}
                  disabled={article.status === '已发布'}
                >
                  {article.status === '已发布' ? '已发布' : '发布文章'}
                </Button>
                <Button 
                  block
                  type="dashed"
                  onClick={() => {
                    const content = editorRef.current?.innerText || '';
                    const wordCount = content.replace(/\s/g, '').length;
                    message.info(`当前字数: ${wordCount} 字`);
                  }}
                >
                  统计字数
                </Button>
                <Button 
                  block
                  type="dashed"
                  onClick={() => {
                    navigator.clipboard.writeText(article.title);
                    message.success('标题已复制到剪贴板');
                  }}
                >
                  复制标题
                </Button>
              </Space>
            </Card>
          </Col>
        </Row>

        {/* 预览模态框 */}
        <Modal
          title="文章预览"
          open={previewVisible}
          onCancel={() => setPreviewVisible(false)}
          width={800}
          footer={null}
          bodyStyle={{ padding: 0 }}
        >
          <div style={{ padding: '24px', maxHeight: '70vh', overflow: 'auto' }}>
            {(() => {
              const previewData = getPreviewContent();
              return (
                <>
                  {/* 文章标题 */}
                  <div style={{ textAlign: 'center', marginBottom: 30 }}>
                    <Title level={2} style={{ marginBottom: 8 }}>
                      {previewData.title}
                    </Title>
                    
                    {/* 文章元信息 */}
                    <Space size="large" style={{ color: '#666' }}>
                      {previewData.author && (
                        <Space size={4}>
                          <UserOutlined />
                          <Text type="secondary">{previewData.author}</Text>
                        </Space>
                      )}
                      
                      {previewData.category && (
                        <Space size={4}>
                          <TagOutlined />
                          <Text type="secondary">{previewData.category}</Text>
                        </Space>
                      )}
                      
                      <Space size={4}>
                        <CalendarOutlined />
                        <Text type="secondary">{previewData.created_time}</Text>
                      </Space>
                      
                      <Tag color={getStatusColor(article?.status || '')}>
                        {article?.status || '草稿'}
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
                    className="article-preview-content"
                  >
                    <style>
                      {`
                        .article-preview-content img {
                          max-width: 100% !important;
                          width: auto !important;
                          height: auto !important;
                          display: block !important;
                          margin: 24px auto !important;
                          border-radius: 8px !important;
                          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
                        }
                        .article-preview-content p {
                          margin: 16px 0 !important;
                          text-align: justify !important;
                        }
                        .article-preview-content h1, .article-preview-content h2, .article-preview-content h3,
                        .article-preview-content h4, .article-preview-content h5, .article-preview-content h6 {
                          margin: 24px 0 16px 0 !important;
                          color: #262626 !important;
                        }
                        .article-preview-content blockquote {
                          margin: 16px 0 !important;
                          padding: 12px 20px !important;
                          background: #f6f8fa !important;
                          border-left: 4px solid #1890ff !important;
                          border-radius: 4px !important;
                        }
                        .article-preview-content ul, .article-preview-content ol {
                          margin: 16px 0 !important;
                          padding-left: 24px !important;
                        }
                        .article-preview-content li {
                          margin: 8px 0 !important;
                        }
                      `}
                    </style>
                    <div dangerouslySetInnerHTML={{ __html: previewData.content }} />
                  </div>

                  {/* 文章统计信息 */}
                  <Divider />
                  <div style={{ textAlign: 'center', color: '#999', fontSize: 14 }}>
                    <Space size="large">
                      <span>字数: {article?.word_count || 0}</span>
                      {article?.public_account_nickname && (
                        <span>公众号: {article.public_account_nickname}</span>
                      )}
                      {article?.saved_status && (
                        <span>存稿状态: {article.saved_status}</span>
                      )}
                    </Space>
                  </div>
                </>
              );
            })()}
          </div>
        </Modal>
      </Card>
    </div>
  );
};

export default ArticleEdit; 