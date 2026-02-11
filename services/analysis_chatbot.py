from typing import Optional, Any
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from analysis_mongo import DrawingAnalysis

async def get_psychology_interpretation_by_category(
    user_id: int,
    category: Any
) -> Optional[dict[str, Any]]:
    """
    특정 사용자의 최신 분석 결과에서 카테고리별 interpretation만 반환
    category: tree, house, man, woman, all
    """

    analysis = await DrawingAnalysis.find(
        DrawingAnalysis.user_id == user_id
    ).sort(-DrawingAnalysis.created_at).first_or_none() # 상위 결과 하나만

    if not analysis:
        return None
    
    target_list = [category] if isinstance(category, str) else category

    interp_data = analysis.psychological_interpretation
    interpret_result = {}

    # all이면 interpretation만 모아서 반환
    if category == "all":
        return {
            key: value.get("interpretation")
            for key, value in interp_data.items()
        }

    # 특정 category
    for c in target_list:
        # interp_data에서 'tree', 'house' 같은 문자열 키로 접근
        category_obj = interp_data.get(c) 
        
        if category_obj and isinstance(category_obj, dict):
            interpret_result[c] = category_obj.get('interpretation')
        else:
            interpret_result[c] = None

    return interpret_result