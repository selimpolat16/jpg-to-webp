import os
from PIL import Image
import warnings
import sys
from datetime import datetime
# Büyük resimler için DecompressionBombWarning uyarısını kapat
warnings.filterwarnings('ignore', '(Possibly )?corrupt EXIF data', UserWarning)
warnings.filterwarnings('ignore', category=Image.DecompressionBombWarning)
# Maksimum piksel limitini yükselt
Image.MAX_IMAGE_PIXELS = None

def get_file_size(file_path):
    """Dosya boyutunu MB cinsinden döndürür"""
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)  # MB cinsinden

def create_log_file():
    """Hata log dosyası oluştur"""
    log_file = f"conversion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return log_file

def log_error(log_file, message):
    """Hata mesajını log dosyasına yaz"""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def convert_to_webp(source_dir='.', quality=80):
    # Log dosyası oluştur
    log_file = create_log_file()
    print(f"Hata logları şu dosyaya kaydedilecek: {log_file}")
    
    # JPG uzantılı dosyaları bul
    jpg_files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.jpeg'))]
    
    if not jpg_files:
        print("Bu dizinde JPG dosyası bulunamadı!")
        return
    
    # webp klasörünü oluştur
    webp_dir = os.path.join(source_dir, 'webp')
    if not os.path.exists(webp_dir):
        os.makedirs(webp_dir)
    
    total_original_size = 0
    total_converted_size = 0
    successful_conversions = 0
    failed_conversions = 0
    
    total_files = len(jpg_files)
    print(f"\nToplam {total_files} dosya bulundu.")
    
    # Her JPG dosyasını WebP'ye dönüştür
    for index, jpg_file in enumerate(jpg_files, 1):
        try:
            # Dosya yollarını oluştur
            input_path = os.path.join(source_dir, jpg_file)
            output_filename = os.path.splitext(jpg_file)[0] + '.webp'
            output_path = os.path.join(webp_dir, output_filename)
            
            # Eğer dosya zaten dönüştürülmüşse atla
            if os.path.exists(output_path):
                print(f"\n{jpg_file} zaten dönüştürülmüş, atlanıyor...")
                continue
            
            # İlerleme durumunu göster
            print(f"\n[{index}/{total_files}] İşleniyor: {jpg_file}")
            
            # Orijinal dosya boyutunu al
            original_size = get_file_size(input_path)
            total_original_size += original_size
            
            print(f"Dosya boyutu: {original_size:.2f}MB")
            
            # Resmi aç ve WebP olarak kaydet
            with Image.open(input_path) as img:
                # Resim boyutlarını göster
                width, height = img.size
                print(f"Resim boyutları: {width}x{height} piksel")
                
                # Resmi kaydet
                img.save(output_path, 'WEBP', quality=quality, method=6)
            
            # Yeni dosya boyutunu al
            converted_size = get_file_size(output_path)
            total_converted_size += converted_size
            
            # Sonuçları yazdır
            saving_percentage = ((original_size - converted_size) / original_size) * 100
            print(f"Dönüştürüldü: {jpg_file} -> {output_filename}")
            print(f"Yeni boyut: {converted_size:.2f}MB")
            print(f"Kazanç: %{saving_percentage:.1f}")
            
            successful_conversions += 1
            
        except Exception as e:
            failed_conversions += 1
            error_msg = f"Hata: {jpg_file} dosyası dönüştürülürken bir sorun oluştu - {str(e)}"
            print(error_msg)
            log_error(log_file, error_msg)
            
            # Eğer yarım kalan bir dosya varsa sil
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
    
    # Final istatistiklerini göster
    print("\n" + "="*50)
    print("DÖNÜŞTÜRME İSTATİSTİKLERİ")
    print("="*50)
    print(f"Toplam dosya sayısı: {total_files}")
    print(f"Başarılı dönüştürmeler: {successful_conversions}")
    print(f"Başarısız dönüştürmeler: {failed_conversions}")
    
    if successful_conversions > 0:
        print("\nBOYUT İSTATİSTİKLERİ")
        print("="*50)
        print(f"Toplam orijinal boyut: {total_original_size:.2f}MB")
        print(f"Toplam yeni boyut: {total_converted_size:.2f}MB")
        total_saving_percentage = ((total_original_size - total_converted_size) / total_original_size) * 100
        print(f"Toplam kazanç: %{total_saving_percentage:.1f}")
    
    if failed_conversions > 0:
        print(f"\nBazı dosyalar dönüştürülemedi. Detaylar için {log_file} dosyasını kontrol edin.")

if __name__ == '__main__':
    try:
        # Kalite parametresi 0-100 arasında olabilir
        # Daha düşük kalite = daha küçük dosya boyutu
        convert_to_webp(quality=80)
    except KeyboardInterrupt:
        print("\nKullanıcı tarafından durduruldu!")
        sys.exit(0)
    except Exception as e:
        print(f"\nBeklenmeyen bir hata oluştu: {str(e)}")
        sys.exit(1) 