# Đây là tool được xây dựng để gán nhãn cho bộ data phục vụ cho việc huấn luyện mô hình của VietOCR

# Yêu cầu

Để sử dụng tool cần có **Python >= 3.7**

## Cài đặt

1. Clone Project này.
2. Chạy lệnh **pip install requirements.txt** để cài đặt các package cần thiết.
3. Chạy lệnh **python main.py** để chạy chương trình

## Hướng dẫn sử dụng

1. Cần tập hợp chung các file ảnh cần gán nhãn vào một folder chung.
2. Click **Choose Image Dir** để mở Dialog và chọn vào folder chứa ảnh cần gán nhãn, có thể xem các ảnh qua lại bằng các click **Prev** hoặc **Next**.
3. Click **Choose Dataset Save Dir** để chọn folder chứa dataset.
4. Chọn **Train Annotation** hoặc **Test Annotation** để lựa chọn tạo **Annotation** cho tập **Train** hoặc tập **Test**.
5. Dùng chuột để vẽ vùng cần gán label, sau khi nhả chuột sẽ hiện 1 form để điền text dự đoán.
6. Sau khi đánh label xong thì ấn **Save** để lưu lại, dữ liệu sẽ được lưu theo cấu trúc để huấn luyện cho VietOCR model, có thể tham khảo cấu trúc [tại đây](https://vocr.vn/data/vietocr/data_line.zip)

## UPDATE

Chương trình đã được build ra file main.exe, có thể chạy luôn bằng file main.exe mà không cần cài đặt các package cần thiết