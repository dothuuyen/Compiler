Chương trình phân tích từ vựng đơn giản cho ngôn ngữ VC

Sử dụng môi trường ảo với python3.7
+ Khởi tạo một môi trường ảo python3.7, nếu lệnh này bị lỗi bạn phải cài đặt virtualenv (`python3 -m pip install --user virtualenv`)

    `python3.7 -m venv venv`

+ Load môi trường ảo

    `source venv/bin/activate`
    
Chạy thử bằng lệnh:

`python lexical.py --input_dfa dfa.dat --input_file test.vc --output_file test.vctok`

Kết quả sẽ output ra file `test.vctok` dưới dạng `token token_type`.

Các tham số dòng lệnh
- `--input_dfa dfa.dat`: Để chạy chương trình cần có file lưu thông tin về automata theo
format được thể hiện trong báo cáo
- `--input_file test.vc`: Mã nguồn chương trình VC để phân tích từ vựng. 
- `--output_file test.vctok`:  Kết quả output của chương trình
- `--debug`: sử dụng cho mục đích debug

Trong trường hợp có lỗi, sẽ in ra số dòng và vị trí trên dòng. Đồng thời bỏ qua phân tích dòng đấy.


 
