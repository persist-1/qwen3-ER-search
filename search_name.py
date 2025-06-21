import fitz  # PyMuPDF
import re

def search_name_in_pdf(pdf_path: str, target_name: str) -> dict:
    """
    在PDF文件中搜索指定姓名
    Args:
        pdf_path: PDF文件路径
        target_name: 要搜索的姓名
    Returns:
        搜索结果字典
    """
    print(f"正在搜索PDF文件: {pdf_path}")
    print(f"目标姓名: {target_name}")
    
    try:
        doc = fitz.open(pdf_path)
        results = {
            "found": False,
            "occurrences": [],
            "total_pages": len(doc),
            "contexts": []
        }
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # 搜索姓名（不区分大小写）
            pattern = re.compile(re.escape(target_name), re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                results["found"] = True
                start_pos = match.start()
                end_pos = match.end()
                
                # 获取上下文（前后50个字符）
                context_start = max(0, start_pos - 50)
                context_end = min(len(text), end_pos + 50)
                context = text[context_start:context_end]
                
                results["occurrences"].append({
                    "page": page_num + 1,
                    "position": start_pos,
                    "context": context.strip()
                })
                
                results["contexts"].append(f"第{page_num + 1}页: {context.strip()}")
        
        doc.close()
        
        return results
        
    except Exception as e:
        print(f"处理PDF文件时出错: {e}")
        return {"found": False, "error": str(e)}

def main():
    pdf_path = r"C:\Users\sanrome\Documents\三郎白底通用简历-zh.pdf"
    target_name = "张三"
    
    print("=== PDF姓名检索系统 ===")
    print(f"PDF文件: {pdf_path}")
    print(f"搜索姓名: {target_name}")
    print("-" * 50)
    
    results = search_name_in_pdf(pdf_path, target_name)
    
    if results.get("error"):
        print(f"错误: {results['error']}")
        return
    
    if results["found"]:
        print(f"✅ 找到姓名 '{target_name}'!")
        print(f"总共在 {len(results['occurrences'])} 个位置找到")
        print(f"PDF总页数: {results['total_pages']}")
        print("\n详细位置:")
        
        for i, occurrence in enumerate(results["occurrences"], 1):
            print(f"\n--- 位置 {i} ---")
            print(f"页码: {occurrence['page']}")
            print(f"上下文: {occurrence['context']}")
    else:
        print(f"❌ 未找到姓名 '{target_name}'")
        print(f"PDF总页数: {results['total_pages']}")
    
    # 额外检查：搜索可能的变体
    print("\n" + "="*50)
    print("额外检查：搜索可能的姓名变体")
    
    variants = ["张三", "三", "张", "三张"]
    for variant in variants:
        if variant != target_name:
            print(f"\n搜索变体: {variant}")
            variant_results = search_name_in_pdf(pdf_path, variant)
            if variant_results["found"]:
                print(f"✅ 找到变体 '{variant}'!")
                for context in variant_results["contexts"]:
                    print(f"  {context}")
            else:
                print(f"❌ 未找到变体 '{variant}'")

if __name__ == "__main__":
    main() 