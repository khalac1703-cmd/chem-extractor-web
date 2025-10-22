import fitz
import os

def extract_images_from_pdf(pdf_path, output_dir="images_out"):
    """
    Trích xuất toàn bộ hình ảnh (sơ đồ, biểu đồ, công thức vẽ) từ file PDF.
    Lưu ra thư mục images_out, đặt tên theo trang và thứ tự.
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    img_metadata = []

    for page_number, page in enumerate(doc, start=1):
        image_list = page.get_images(full=True)
        print(f"Trang {page_number}: {len(image_list)} hình ảnh được phát hiện.")

        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"page{page_number}_img{img_index}.{image_ext}"

            image_path = os.path.join(output_dir, image_name)
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            img_metadata.append({
                "page": page_number,
                "path": image_path,
                "xref": xref
            })

    doc.close()
    print(f"\n✅ Đã trích xuất {len(img_metadata)} hình ảnh. Kết quả lưu tại: {output_dir}")
    return img_metadata


# ----------- CHẠY THỬ NGHIỆM -----------
if __name__ == "__main__":
    pdf_file = "live-46-bai-toan-thuc-te-san-xuat-tong-hop-polymer-b616cb5a-1126-4ba3-a2b6-6a1b61d1a08d.pdf"
    extract_images_from_pdf(pdf_file)
