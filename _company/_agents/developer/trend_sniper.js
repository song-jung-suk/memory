const axios = require('axios');
const fs = require('fs');

// API 설정
const BASE_URL = 'https://api.taoxiaohu.com/v1'; // 1688 예시 URL (실제 API 키를 환경 변수로 처리)
const API_KEY = process.env.TOAUBAO_API_KEY || '';

async function getTrendData() {
    try {
        const response = await axios.get(BASE_URL, {
            headers: { 'X-API-Key': API_KEY }
        });
        
        console.log('trend_sniper.js 실행 완료:', JSON.stringify(response.data));
        fs.writeFileSync(
            `e:/work_company/sessions/trend_sniper_2026-06-07.json`, 
            JSON.stringify(response.data)
        );
        return true;
    } catch (error) {
        console.error('trend_sniper.js 실행 오류:', error.message);
        fs.writeFileSync(
            `e:/work_company/sessions/trend_sniper_2026-06-07_error.json`, 
            JSON.stringify({ error: error.message })
        );
        return false;
    }
}

// 실행
getTrendData();