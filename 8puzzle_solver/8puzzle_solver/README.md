# 8 Puzzle Solver

Bài toán 8-Puzzle giải bằng các thuật toán tìm kiếm cơ bản.

## Yêu cầu

- Python 3.x (tkinter có sẵn trong Python)
- Không cần cài thêm thư viện nào

## Cách chạy

```bash
cd 8puzzle_solver
python main.py
```

## Các thuật toán

| Thuật toán | Mô tả |
|---|---|
| **BFS** | Breadth-First Search - Tìm kiếm theo chiều rộng, dùng FIFO queue |
| **DFS** | Depth-First Search - Tìm kiếm theo chiều sâu, dùng LIFO stack |
| **DLS** | Depth-Limited Search - DFS với giới hạn độ sâu |
| **IDS** | Iterative Deepening Search - Lặp DLS với limit tăng dần |
| **UCS** | Uniform Cost Search - Tìm kiếm theo chi phí, dùng priority queue |

## Cấu trúc project

```
8puzzle_solver/
├── main.py              # Giao diện chính (tkinter)
├── algorithms/
│   ├── __init__.py
│   ├── utils.py         # Hàm dùng chung
│   ├── bfs.py           # BFS
│   ├── dfs.py           # DFS
│   ├── dls.py           # DLS
│   ├── ids.py           # IDS
│   └── ucs.py           # UCS
└── README.md
```

## Hướng dẫn sử dụng

1. Nhấn **Shuffle** để tạo trạng thái ngẫu nhiên (đảm bảo có lời giải)
2. Chọn thuật toán từ dropdown
3. Với **DLS**: nhập thêm giới hạn độ sâu
4. Nhấn **SOLVE** để tìm lời giải
5. Xem các bước ở panel bên phải
6. Dùng **Prev / Next** hoặc **Auto** để duyệt từng bước
