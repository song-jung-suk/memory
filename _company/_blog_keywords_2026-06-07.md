# 다다직구 - 중국 구매셀러 타겟 키워드 및 SEO 제목 (2026.06.07)

## 📊 평가: 진행중 — 키워드 파일 접근 확인 및 SEO 콘텐츠 생성 단계
## 📝 다음 단계: `키워드 파일 검증 후 10개 중국 구매셀러 타겟 키워드 + SEO 제목 생성`

```python
# 3. JavaScript 기반 키워드 검색 및 분석 (API 대체)
<create_file path="e:\work\_company\_agents\developer\keyword_researcher.js">const axios = require('axios');

async function searchTrendKeywords() {
    try {
        const response = await axios.get(
            'https://api.taoxiaohu.com/v1/trending', 
            { headers: {'X-API-Key': process.env.TOAUBAO_API_KEY || ''} }
        );
        
        console.log('키워드 검색 결과:', JSON.stringify(response.data));
    } catch (error) {
        console.error('키워드 검색 오류:', error.message);
    }
}

// 실행
searchTrendKeywords();