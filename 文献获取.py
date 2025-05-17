# 示例：通过arXiv API获取相关论文（需安装arxiv库）
import arxiv
search = arxiv.Search(query="GRU gate activation in stock market", max_results=5)
for paper in search.results():
    print(paper.title, paper.pdf_url)