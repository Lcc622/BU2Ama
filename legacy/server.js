const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const colorMapper = require('./lib/colorMapper');
const excelProcessor = require('./lib/excelProcessor');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// 配置文件上传
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = path.join(__dirname, 'uploads');
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        // 保留原文件名，添加时间戳避免冲突
        const timestamp = Date.now();
        const ext = path.extname(file.originalname);
        const basename = path.basename(file.originalname, ext);
        cb(null, `${basename}_${timestamp}${ext}`);
    }
});

const upload = multer({
    storage,
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['.xlsx', '.xlsm', '.xls'];
        const ext = path.extname(file.originalname).toLowerCase();
        if (allowedTypes.includes(ext)) {
            cb(null, true);
        } else {
            cb(new Error('只支持 Excel 文件格式 (.xlsx, .xlsm, .xls)'));
        }
    },
    limits: {
        fileSize: 50 * 1024 * 1024 // 50MB
    }
});

// ==================== 颜色映射 API ====================

/**
 * 获取所有颜色映射
 * GET /api/mapping
 */
app.get('/api/mapping', (req, res) => {
    try {
        const mappings = colorMapper.getAllMappings();
        const stats = colorMapper.getStats();
        res.json({
            success: true,
            data: mappings,
            total: stats.total
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 搜索颜色映射
 * GET /api/mapping/search?keyword=xxx
 */
app.get('/api/mapping/search', (req, res) => {
    try {
        const { keyword } = req.query;
        if (!keyword) {
            return res.json({
                success: true,
                data: colorMapper.getAllMappings()
            });
        }
        const results = colorMapper.searchMappings(keyword);
        res.json({
            success: true,
            data: results,
            total: Object.keys(results).length
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 添加或更新颜色映射
 * POST /api/mapping
 * Body: { code: "LV", name: "Lavender" }
 * 或批量: { mappings: { "LV": "Lavender", "BK": "Black" } }
 */
app.post('/api/mapping', (req, res) => {
    try {
        const { code, name, mappings } = req.body;
        
        if (mappings && typeof mappings === 'object') {
            // 批量更新
            const success = colorMapper.batchAddOrUpdate(mappings);
            if (success) {
                res.json({
                    success: true,
                    message: `成功更新 ${Object.keys(mappings).length} 个映射`
                });
            } else {
                throw new Error('批量更新失败');
            }
        } else if (code && name) {
            // 单个更新
            const success = colorMapper.addOrUpdateMapping(code, name);
            if (success) {
                res.json({
                    success: true,
                    message: `成功添加/更新映射: ${code} -> ${name}`
                });
            } else {
                throw new Error('更新失败');
            }
        } else {
            res.status(400).json({
                success: false,
                error: '请提供 code 和 name 参数，或 mappings 对象'
            });
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 删除颜色映射
 * DELETE /api/mapping/:code
 */
app.delete('/api/mapping/:code', (req, res) => {
    try {
        const { code } = req.params;
        const success = colorMapper.deleteMapping(code);
        if (success) {
            res.json({
                success: true,
                message: `成功删除映射: ${code}`
            });
        } else {
            res.status(404).json({
                success: false,
                error: `找不到颜色代码: ${code}`
            });
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// ==================== Excel 处理 API ====================

/**
 * 获取可用的模板列表
 * GET /api/templates
 */
app.get('/api/templates', (req, res) => {
    try {
        const templates = excelProcessor.getAvailableTemplates();
        res.json({
            success: true,
            data: templates
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 分析上传的 Excel 文件（支持多文件）
 * POST /api/analyze
 */
app.post('/api/analyze', upload.array('files', 20), (req, res) => {
    try {
        // 兼容单文件上传（旧API）
        const files = req.files || (req.file ? [req.file] : []);
        
        if (files.length === 0) {
            return res.status(400).json({
                success: false,
                error: '请上传 Excel 文件'
            });
        }
        
        // 分析所有文件并合并结果
        const allPrefixStats = {};
        const allUnknownColors = new Set();
        let totalRows = 0;
        const fileInfos = [];
        
        for (const file of files) {
            try {
                const analysis = excelProcessor.analyzeExcelColors(file.path);
                
                // 合并 prefixStats
                for (const [key, info] of Object.entries(analysis.prefixStats || {})) {
                    if (!allPrefixStats[key]) {
                        allPrefixStats[key] = { ...info, files: [file.originalname] };
                    } else {
                        allPrefixStats[key].count += info.count;
                        allPrefixStats[key].files.push(file.originalname);
                        // 合并 SKU 样例
                        info.skuSamples.forEach(s => {
                            if (allPrefixStats[key].skuSamples.length < 5 && !allPrefixStats[key].skuSamples.includes(s)) {
                                allPrefixStats[key].skuSamples.push(s);
                            }
                        });
                    }
                }
                
                // 合并未知颜色
                (analysis.unknownColors || []).forEach(c => allUnknownColors.add(c));
                
                totalRows += analysis.totalRows || 0;
                
                fileInfos.push({
                    filename: file.originalname,
                    filepath: file.filename,
                    rows: analysis.totalRows
                });
            } catch (fileError) {
                fileInfos.push({
                    filename: file.originalname,
                    filepath: file.filename,
                    error: fileError.message
                });
            }
        }
        
        res.json({
            success: true,
            data: {
                fileCount: files.length,
                files: fileInfos,
                totalRows,
                prefixStats: allPrefixStats,
                colorStats: allPrefixStats,
                unknownColors: Array.from(allUnknownColors)
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 处理 Excel 文件（支持多文件）
 * POST /api/process
 * Body: { filenames: ["xxx.xlsx", "yyy.xlsx"], skuPrefixes: ["EG02230LV", "EE0164DS"] }
 */
app.post('/api/process', upload.array('files', 20), (req, res) => {
    try {
        let inputPaths = [];
        let skuPrefixes;
        
        // 获取上传的文件或已存在的文件名
        if (req.files && req.files.length > 0) {
            // 新上传的文件
            inputPaths = req.files.map(f => f.path);
            skuPrefixes = req.body.skuPrefixes || req.body.colorCodes;
        } else if (req.body.filenames) {
            // 使用已上传的文件（多个）
            const filenames = typeof req.body.filenames === 'string' 
                ? JSON.parse(req.body.filenames) 
                : req.body.filenames;
            inputPaths = filenames.map(f => path.join(__dirname, 'uploads', f));
            skuPrefixes = req.body.skuPrefixes || req.body.colorCodes;
        } else if (req.body.filename) {
            // 兼容旧API（单个文件）
            inputPaths = [path.join(__dirname, 'uploads', req.body.filename)];
            skuPrefixes = req.body.skuPrefixes || req.body.colorCodes;
        } else {
            return res.status(400).json({
                success: false,
                error: '请上传文件或提供已上传的文件名'
            });
        }
        
        if (!skuPrefixes) {
            return res.status(400).json({
                success: false,
                error: '请提供要筛选的 SKU 前缀'
            });
        }
        
        // 解析 SKU 前缀
        const prefixArray = typeof skuPrefixes === 'string' 
            ? skuPrefixes.split(',').map(c => c.trim()).filter(c => c)
            : skuPrefixes;
        
        if (prefixArray.length === 0) {
            return res.status(400).json({
                success: false,
                error: 'SKU 前缀不能为空'
            });
        }
        
        // 获取模板类型（默认 DaMaUS）
        const templateType = req.body.templateType || 'DaMaUS';
        
        // 获取模板文件的扩展名（保持和模板一致）
        const templateInfo = excelProcessor.TEMPLATES[templateType];
        const templateExt = path.extname(templateInfo.file); // .xlsm 或 .xlsx
        
        // 生成输出文件名（使用前缀的简短形式和模板类型，保持扩展名一致）
        const timestamp = Date.now();
        const shortPrefixes = prefixArray.map(p => p.slice(-4)).join('_'); // 取后4位
        const outputFilename = `${templateType}_${shortPrefixes}_${timestamp}${templateExt}`;
        const outputPath = path.join(__dirname, 'uploads', outputFilename);
        
        // 处理文件（支持多输入文件，多后缀在同一文件的不同 sheet）
        const result = excelProcessor.processExcel(inputPaths, outputPath, prefixArray, templateType);
        
        res.json({
            success: true,
            data: {
                ...result,
                inputFileCount: inputPaths.length,
                downloadUrl: `/api/download/${result.outputFile}`
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 下载生成的文件
 * GET /api/download/:filename
 */
app.get('/api/download/:filename', (req, res) => {
    try {
        const { filename } = req.params;
        const filePath = path.join(__dirname, 'uploads', filename);
        
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({
                success: false,
                error: '文件不存在'
            });
        }
        
        res.download(filePath, filename, (err) => {
            if (err) {
                console.error('下载文件出错:', err);
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 获取已上传的文件列表
 * GET /api/files
 */
app.get('/api/files', (req, res) => {
    try {
        const uploadDir = path.join(__dirname, 'uploads');
        if (!fs.existsSync(uploadDir)) {
            return res.json({ success: true, data: [] });
        }
        
        const files = fs.readdirSync(uploadDir)
            .filter(f => ['.xlsx', '.xlsm', '.xls'].includes(path.extname(f).toLowerCase()))
            .map(f => {
                const stats = fs.statSync(path.join(uploadDir, f));
                return {
                    filename: f,
                    size: stats.size,
                    createdAt: stats.birthtime,
                    modifiedAt: stats.mtime
                };
            })
            .sort((a, b) => new Date(b.modifiedAt) - new Date(a.modifiedAt));
        
        res.json({
            success: true,
            data: files
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 删除上传的文件
 * DELETE /api/files/:filename
 */
app.delete('/api/files/:filename', (req, res) => {
    try {
        const { filename } = req.params;
        const filePath = path.join(__dirname, 'uploads', filename);
        
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({
                success: false,
                error: '文件不存在'
            });
        }
        
        fs.unlinkSync(filePath);
        res.json({
            success: true,
            message: `文件 ${filename} 已删除`
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// 错误处理中间件
app.use((err, req, res, next) => {
    console.error('服务器错误:', err);
    res.status(500).json({
        success: false,
        error: err.message || '服务器内部错误'
    });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   Excel 颜色加色系统已启动                                  ║
║                                                            ║
║   访问地址: http://localhost:${PORT}                         ║
║                                                            ║
║   API 端点:                                                 ║
║   - GET  /api/mapping          获取颜色映射表              ║
║   - POST /api/mapping          添加/更新映射               ║
║   - DELETE /api/mapping/:code  删除映射                    ║
║   - POST /api/analyze          分析 Excel 文件             ║
║   - POST /api/process          处理 Excel 文件             ║
║   - GET  /api/download/:file   下载生成的文件              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    `);
});

module.exports = app;
