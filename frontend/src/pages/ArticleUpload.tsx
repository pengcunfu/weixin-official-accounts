import React, { useState, useEffect } from 'react';
import { Card, Upload, Button, Space, Progress, Alert, List, Tag, message, Select, Form } from 'antd';
import { UploadOutlined, InboxOutlined, CheckCircleOutlined, ExclamationCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { UploadResult, PublicAccount } from '../types';
import { uploadService } from '../services/uploadService';
import { accountService } from '../services/accountService';
import { useNavigate } from 'react-router-dom';

const { Dragger } = Upload;
const { Option } = Select;

const ArticleUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);
  const [fileList, setFileList] = useState<any[]>([]);
  const [publicAccounts, setPublicAccounts] = useState<PublicAccount[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<number | undefined>();
  const [form] = Form.useForm();
  const navigate = useNavigate();

  // 加载公众号列表
  useEffect(() => {
    const loadAccounts = async () => {
      try {
        const response = await accountService.getAccountList({ page: 1, limit: 100 });
        if (response.data?.data) {
          setPublicAccounts(response.data.data);
        }
      } catch (error) {
        // 错误已在 api.ts 中统一处理
        console.error('加载公众号列表失败:', error);
      }
    };
    loadAccounts();
  }, []);

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择要上传的文件');
      return;
    }

    if (!selectedAccountId) {
      message.warning('请先选择公众号');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setUploadResults([]);

    const results: UploadResult[] = [];
    const totalFiles = fileList.length;

    try {
      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        const progress = Math.round(((i + 1) / totalFiles) * 100);
        setUploadProgress(progress);

        try {
          // 上传文档文件（后端会自动创建文章）
          const uploadResponse = await uploadService.uploadDocument(file.originFileObj, selectedAccountId);
          const articleInfo = uploadResponse.data?.article;
              results.push({
                filename: file.name,
                status: 'success',
            message: '上传并创建文章成功',
            title: articleInfo?.title || file.name.replace(/\.[^/.]+$/, ""),
                word_count: 0,
                images_count: 0
              });
        } catch (fileError: any) {
          results.push({
            filename: file.name,
            status: 'error',
            message: `上传失败: ${fileError.message || '网络错误'}`
          });
        }
      }

      setUploadResults(results);
      const successCount = results.filter(r => r.status === 'success').length;
      
      if (successCount > 0) {
        message.success(`成功上传 ${successCount} 个文件`);
      } else {
        message.error('所有文件上传失败');
      }
      
      // 清空文件列表
      setFileList([]);
    } catch (error: any) {
      // 错误已在 api.ts 中统一处理
    } finally {
      setUploading(false);
      setUploadProgress(100);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const beforeUpload = (file: any) => {
    const isDocx = file.name.toLowerCase().endsWith('.docx');
    if (!isDocx) {
      message.error('只能上传 .docx 格式的文件');
      return false;
    }

    const isLt50M = file.size / 1024 / 1024 < 50;
    if (!isLt50M) {
      message.error('文件大小不能超过 50MB');
      return false;
    }

    return false; // 阻止自动上传
  };

  const uploadProps = {
    multiple: true,
    fileList,
    beforeUpload,
    onChange: ({ fileList: newFileList }: any) => {
      setFileList(newFileList);
    },
    onRemove: (file: any) => {
      const index = fileList.indexOf(file);
      const newFileList = fileList.slice();
      newFileList.splice(index, 1);
      setFileList(newFileList);
    },
  };

  const getResultIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'warning':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return null;
    }
  };

  const getResultColor = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getResultText = (status: string) => {
    switch (status) {
      case 'success': return '成功';
      case 'warning': return '警告';
      case 'error': return '失败';
      default: return '未知';
    }
  };

  const getUploadSummary = () => {
    const successCount = uploadResults.filter(item => item.status === 'success').length;
    const warningCount = uploadResults.filter(item => item.status === 'warning').length;
    const errorCount = uploadResults.filter(item => item.status === 'error').length;

    return { successCount, warningCount, errorCount };
  };

  const { successCount, warningCount, errorCount } = getUploadSummary();

  return (
    <div>
      <Card
        title="文章上传"
        extra={
          <Space>
            <Button onClick={() => navigate('/articles')}>
              返回文章列表
            </Button>
          </Space>
        }
      >
        {/* 公众号选择 */}
        <Card size="small" style={{ marginBottom: 24 }}>
          <Form form={form} layout="inline">
            <Form.Item
              label="选择公众号"
              name="public_account_id"
              rules={[{ required: true, message: '请选择公众号' }]}
              style={{ minWidth: 300 }}
            >
              <Select
                placeholder="请选择要关联的公众号"
                value={selectedAccountId}
                onChange={setSelectedAccountId}
                style={{ width: '100%' }}
                showSearch
                optionFilterProp="children"
              >
                {publicAccounts.map(account => (
                  <Option key={account.id} value={account.id}>
                    <Space>
                      <span>{account.nickname || account.name}</span>
                      <Tag color={account.authorized ? 'success' : 'default'}>
                        {account.authorized ? '已授权' : '未授权'}
                      </Tag>
                    </Space>
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Form>
        </Card>

        {/* 上传区域 */}
        <Dragger
          {...uploadProps}
          style={{ marginBottom: 24 }}
          disabled={uploading || !selectedAccountId}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: 48, color: selectedAccountId ? '#1890ff' : '#ccc' }} />
          </p>
          <p className="ant-upload-text">
            {selectedAccountId ? '点击或拖拽文件到此区域上传' : '请先选择公众号'}
          </p>
          <p className="ant-upload-hint">
            支持单个或批量上传 .docx 格式的文件，每个文件大小不超过 50MB
          </p>
        </Dragger>

        {/* 文件列表和上传按钮 */}
        {fileList.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <div style={{ marginBottom: 16 }}>
              <Space>
                <span>已选择 {fileList.length} 个文件</span>
                {selectedAccountId && (
                  <Tag color="blue">
                    目标公众号: {publicAccounts.find(a => a.id === selectedAccountId)?.nickname || 
                                publicAccounts.find(a => a.id === selectedAccountId)?.name}
                  </Tag>
                )}
                <Button
                  type="primary"
                  icon={<UploadOutlined />}
                  loading={uploading}
                  onClick={handleUpload}
                  disabled={!selectedAccountId}
                >
                  {uploading ? '上传中...' : '开始上传'}
                </Button>
                <Button
                  onClick={() => setFileList([])}
                  disabled={uploading}
                >
                  清空列表
                </Button>
              </Space>
            </div>

            {/* 上传进度 */}
            {uploading && (
              <div style={{ marginBottom: 16 }}>
                <Progress 
                  percent={uploadProgress} 
                  status={uploadProgress === 100 ? 'success' : 'active'}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* 上传结果 */}
        {uploadResults.length > 0 && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Alert
                message="上传完成"
                description={
                  <div>
                    <p>上传结果统计：</p>
                    <Space>
                      {successCount > 0 && (
                        <Tag color="success" icon={<CheckCircleOutlined />}>
                          成功 {successCount} 个
                        </Tag>
                      )}
                      {warningCount > 0 && (
                        <Tag color="warning" icon={<ExclamationCircleOutlined />}>
                          警告 {warningCount} 个
                        </Tag>
                      )}
                      {errorCount > 0 && (
                        <Tag color="error" icon={<CloseCircleOutlined />}>
                          失败 {errorCount} 个
                        </Tag>
                      )}
                    </Space>
                  </div>
                }
                type={errorCount > 0 ? 'error' : warningCount > 0 ? 'warning' : 'success'}
                showIcon
              />
            </div>

            <List
              header={<div><strong>上传详情</strong></div>}
              bordered
              dataSource={uploadResults}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getResultIcon(item.status)}
                    title={
                      <Space>
                        <span>{item.filename}</span>
                        <Tag color={getResultColor(item.status)}>
                          {getResultText(item.status)}
                        </Tag>
                        {item.title && (
                          <Tag color="blue">{item.title}</Tag>
                        )}
                      </Space>
                    }
                    description={
                      <div>
                        {item.message && <div>{item.message}</div>}
                        {item.status === 'success' && (
                          <Space size="large">
                            <span>文章已创建</span>
                            {item.author && <span>作者: {item.author}</span>}
                            {item.word_count && item.word_count > 0 && <span>字数: {item.word_count}</span>}
                            {item.images_count && item.images_count > 0 && <span>图片: {item.images_count} 张</span>}
                          </Space>
                        )}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />

            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Button
                type="primary"
                onClick={() => navigate('/articles')}
              >
                查看文章列表
              </Button>
            </div>
          </div>
        )}

        {/* 使用说明 */}
        <Card 
          title="使用说明" 
          size="small" 
          style={{ marginTop: 24, background: '#fafafa' }}
        >
          <div>
            <h4>支持的文件格式：</h4>
            <ul>
              <li>.docx 格式的 Word 文档</li>
              <li>文件大小不超过 50MB</li>
            </ul>

            <h4>上传功能：</h4>
            <ul>
              <li>支持拖拽上传和点击选择</li>
              <li>支持批量上传多个文件</li>
              <li>自动解析文档内容、标题、作者等信息</li>
              <li>自动提取文档中的图片</li>
              <li>自动关联选择的公众号</li>
            </ul>

            <h4>注意事项：</h4>
            <ul>
              <li>上传前必须先选择要关联的公众号</li>
              <li>请确保文档格式正确，避免上传失败</li>
              <li>文档中的图片会自动上传到服务器</li>
              <li>上传成功后可在文章列表中查看和编辑</li>
              <li>文章将自动关联到所选的公众号</li>
            </ul>
          </div>
        </Card>
      </Card>
    </div>
  );
};

export default ArticleUpload; 