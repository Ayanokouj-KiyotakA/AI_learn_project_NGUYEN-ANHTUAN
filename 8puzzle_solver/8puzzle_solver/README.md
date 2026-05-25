# 8 Puzzle Solver

Bài toán 8-Puzzle giải bằng các thuật toán tìm kiếm cơ bản.

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
