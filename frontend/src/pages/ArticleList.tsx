import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Space, Card, message, Modal, Input, Select, Tag } from 'antd';
import { EditOutlined, DeleteOutlined, UploadOutlined, SearchOutlined, EyeOutlined } from '@ant-design/icons';
import { Article, PaginationParams } from '../types';
import { articleService } from '../services/articleService';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';

const { Option } = Select;
const { Search } = Input;

const ArticleList: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useState<PaginationParams>({
    page: 1,
    limit: 10,
    title: '',
  });
  const [total, setTotal] = useState(0);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const navigate = useNavigate();

  const loadArticles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await articleService.getArticleList(searchParams);
      setArticles(response.data?.data || []);
      setTotal(response.data?.total || 0);
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  const handleSearch = (value: string) => {
    setSearchParams(prev => ({
      ...prev,
      page: 1,
      title: value,
    }));
  };

  const handleEdit = (article: Article) => {
    navigate(`/articles/edit/${article.id}`);
  };

  const handlePreview = (article: Article) => {
    window.open(`/articles/preview/${article.id}`, '_blank');
  };

  const handleDelete = (article: Article) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文章 "${article.title}" 吗？`,
      onOk: async () => {
        try {
          await articleService.deleteArticle(article.id);
          message.success('删除成功');
          loadArticles();
        } catch (error) {
          // 错误已在 api.ts 中统一处理
        }
      },
    });
  };

  const handleBatchDelete = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的文章');
      return;
    }

    Modal.confirm({
      title: '批量删除',
      content: `确定要删除选中的 ${selectedRowKeys.length} 篇文章吗？`,
      onOk: async () => {
        try {
          const idsString = selectedRowKeys.join(',');
          await articleService.batchDeleteArticles(idsString);
          message.success('批量删除成功');
          setSelectedRowKeys([]);
          loadArticles();
        } catch (error) {
          // 错误已在 api.ts 中统一处理
        }
      },
    });
  };

  const handleBatchSave = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要保存的文章');
      return;
    }

    Modal.confirm({
      title: '批量保存',
      content: `确定要保存选中的 ${selectedRowKeys.length} 篇文章到微信公众号吗？`,
      onOk: async () => {
        try {
          let successCount = 0;
          let failCount = 0;
          
          for (const id of selectedRowKeys) {
            try {
              await articleService.saveToAccount(Number(id));
              successCount++;
            } catch (error) {
              failCount++;
            }
          }
          
          if (successCount > 0) {
            message.success(`批量保存完成！成功: ${successCount}，失败: ${failCount}`);
            setSelectedRowKeys([]);
            loadArticles();
          } else {
            message.error('批量保存失败，所有文章都保存失败');
          }
        } catch (error) {
          // 错误已在 api.ts 中统一处理
        }
      },
    });
  };

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

  const getSavedStatusColor = (status: string) => {
    switch (status) {
      case '已存稿': return 'success';
      case '未存稿': return 'default';
      case '存稿中': return 'processing';
      case '存稿失败': return 'error';
      default: return 'default';
    }
  };

  const getSavedStatusText = (status: string) => {
    return status || '未存稿';
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
    },
    {
      title: '文件类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 100,
      render: (type: string) => (
        <Tag color="blue">{type?.toUpperCase()}</Tag>
      ),
    },
    {
      title: '字数',
      dataIndex: 'word_count',
      key: 'word_count',
      width: 80,
      render: (count: number) => count ? `${count}字` : '-',
    },
    {
      title: '作者',
      dataIndex: 'author_nickname',
      key: 'author_nickname',
      width: 120,
    },
    {
      title: '公众号',
      dataIndex: 'public_account_nickname',
      key: 'public_account_nickname',
      width: 150,
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '保存状态',
      dataIndex: 'saved_status',
      key: 'saved_status',
      width: 100,
      render: (status: string) => (
        <Tag color={getSavedStatusColor(status)}>
          {getSavedStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_time',
      key: 'created_time',
      width: 150,
      render: (time: string) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (record: Article) => (
        <Space>
          <Button 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button 
            type="primary" 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button 
            danger 
            size="small" 
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => {
      setSelectedRowKeys(keys);
    },
  };

  return (
    <div>
      <Card>
        {/* 搜索栏和操作按钮 */}
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Search
              placeholder="搜索文章标题"
              allowClear
              style={{ width: 300 }}
              onSearch={handleSearch}
              enterButton={<SearchOutlined />}
            />
            <Select
              placeholder="选择分类"
              style={{ width: 150 }}
              allowClear
              onChange={(value) => setSearchParams(prev => ({ ...prev, page: 1, category: value }))}
            >
              <Option value="科技">科技</Option>
              <Option value="生活">生活</Option>
              <Option value="教育">教育</Option>
              <Option value="娱乐">娱乐</Option>
            </Select>
          </Space>
          <Button 
            type="primary" 
            icon={<UploadOutlined />}
            onClick={() => navigate('/articles/upload')}
          >
            上传文章
          </Button>
        </div>

        {/* 批量操作栏 */}
        {selectedRowKeys.length > 0 && (
          <div style={{ marginBottom: 16, padding: 12, background: '#f0f2f5', borderRadius: 6 }}>
            <Space>
              <span>已选择 {selectedRowKeys.length} 项</span>
              <Button 
                type="primary" 
                size="small"
                onClick={handleBatchSave}
              >
                批量保存到公众号
              </Button>
              <Button 
                danger 
                size="small"
                onClick={handleBatchDelete}
              >
                批量删除
              </Button>
              <Button 
                size="small"
                onClick={() => setSelectedRowKeys([])}
              >
                取消选择
              </Button>
            </Space>
          </div>
        )}

        <Table
          columns={columns}
          dataSource={articles}
          rowKey="id"
          loading={loading}
          rowSelection={rowSelection}
          scroll={{ x: 1200 }}
          pagination={{
            current: searchParams.page,
            pageSize: searchParams.limit,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setSearchParams(prev => ({
                ...prev,
                page,
                limit: pageSize || 10,
              }));
            },
          }}
        />
      </Card>
    </div>
  );
};

export default ArticleList; 