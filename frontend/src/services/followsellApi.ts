import axios from '@/lib/axios';

export const followsellApi = {
  /**
   * 处理跟卖上新
   * @param file 老版本 Excel 文件
   * @param newProductCode 新产品代码
   * @returns 处理结果
   */
  process: async (file: File, newProductCode: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('new_product_code', newProductCode);

    const response = await axios.post('/api/followsell/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * 下载生成的文件
   * @param filename 文件名
   * @returns Blob 对象
   */
  download: async (filename: string) => {
    const response = await axios.get(`/api/followsell/download/${filename}`, {
      responseType: 'blob',
    });

    return response.data;
  },
};
