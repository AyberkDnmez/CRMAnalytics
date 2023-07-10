# Başlık : RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)

# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veri Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# 7. Tüm Sürecin Fonksiyonlaştırılması

#################################################
# 1. İş Problemi (Business Problem)
#################################################

# İş Problemi: Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi: Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasında satışlarını içeriyor.

# Değişkenler
#
# InvoiceNo: Fatura Numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi.
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası.
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

#################################################
# 2. Veriyi Anlama (Data Understanding)
#################################################

import datetime as dt
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: '%.3f' % x)

df_ = pd.read_excel(r"C:\Users\user\PycharmProjects\pythonProject3\online_retail_II.xlsx", sheet_name="Year 2009-2010")

# Herhangi bir noktada ana veri setine geri dönüş yapmak isteyebiliriz. Bu noktada yukarıdaki excel dosyasının okunması uzun sürecektir. Bundan dolayı aşağıdaki kodu yazarak zaman kazanabiliriz.

df = df_.copy()
df.head()
df.shape
df.isnull().sum()

# eşsiz ürün sayısı nedir ?
df["Description"].nunique()

# hangi ürün kaç kere satışa konu olmuştur ? (bu kısmı iyi anlamadım.)
df["Description"].value_counts().head()

# hangi üründen kaçar tane satılmıştır ?
# aşağıdaki kodda quantityler eksi değerde gözükmektedir. veri ön işleme kısmında bu problem ortadan kaldırılacaktır.

df.groupby("Description").agg({"Quantity":"sum"}).head()

# ana amacımıza dönelim ve quantitylere göre küçükten büyüğe doğru sıralayalım.

df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity", ascending=False).head()

# kaç tane eşsiz fatura kesilmiştir ?
df["Invoice"].nunique()

# her bir üründen elde edilen geliri bulmak için

df["Total Price"] = df["Quantity"] * df["Price"]

# fatura başı geliri bulmak için
df.groupby("Invoice").agg({"Total Price": "sum"}).head()

# Başlık : Veriyi Hazırlama (Data Preparation)

# 3. Veri Hazırlama (Data Preparation)

# Verinin yapısını hatırlayalım
df.shape

# Hangi değişkende kaç eksik değer var ?
df.isnull().sum()

# Eksik değerleri silmek için aşağıdaki kodu kullanırız.
df.dropna(inplace=True)

df.shape

df.describe().T

# Yukarıdaki kodu çalıştırdığımızda görüleceği üzere iade faturalar bazı değerlerde anormalliğe yol açmaktadır. Bu yüzden iade faturaları da veri setinden çıkarmamız gerekmektedir.

# İade faturaları dışındaki faturaları seçmek için:
df[~df["Invoice"].str.contains("C", na=False)]

# İade faturalarını (başında C olanlar) seçmek isteseydik tilda işaretini kaldırmamız gerekirdi.
df[df["Invoice"].str.contains("C", na=False)]

df = df[~df["Invoice"].str.contains("C", na=False)]

# Başlık : RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)

# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)

# Recency, Frequency, Monetary
df.head()

# Bu aşamada yapmamız gereken her bir müşteri özelinde bu recency, frequency, ve monetary değerlerini hesaplamak olacaktır.

# Recency = Analizin yapıldığı tarih - Müşterinin alışveriş yaptığı son tarih

# Öncelikle analizin yapıldığı günü belirlememiz gerekmektedir.

# Veri setimiz 2009-2011 yılları arasında oluşturulan bir veri setidir. Dolayısıyla analizi o yıllarda yapmadığımız için şöyle bir yol izlememiz gerekmektedir : İlgili hesaplamaların yapılması için analizin yapıldığı günü tanımlamamız gerekmektedir.

# Bunu nasıl yapabiliriz ? Örneğin bu veri seti içerisindeki en son tarih hangi tarihse örneğin bu tarihin üzerine 2 gün koyarız.

df["InvoiceDate"].max()

# Bunu yapmak için datetime kütüphanesini kullanırız.

today_date = dt.datetime(2010, 12, 11)
type(today_date)

# Yukarıda yaptığımız işlem aşağıdaki yapacağımız işlemlerde zaman açısından fark alabilmemizi sağlayacaktır.

# RFM analizi en basit haliyle bir pandas operasyonudur.

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     "Invoice": lambda Invoice: Invoice.nunique(),
                                     "Total Price": lambda TotalPrice: TotalPrice.sum()})

rfm.head()

# Rfm tablomuzdaki isimlendirmeleri değiştirelim.

rfm.columns = ["recency", "frequency", "monetary"]

rfm

rfm.describe().T

# Monetarydeki min değerinin 0 olması mantıklı olmadığından dolayı o değeri silmemiz gerekmektedir. Seçme işlemini bu şekilde gerçekleştirebiliriz.

rfm = rfm[rfm["monetary"] > 0]

rfm.describe().T
rfm.shape

# Şimdi elimizdeki metrikleri skorlara dönüştürmemiz gerekir.

# Başlık : RFM Skorlarının Hesaplanması (Calculating RFM Scores)

# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)

# Recency, frequency ve monetary değerlerini skorlara çevireceğiz.

# Recency skorundan başlayalım. qcut fonksiyonu işimizi görecektir. qcut fonksiyonu değişken değerlerini küçükten büyüğe sıralar ve belirli parçalara göre bunu böler.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])

# Monetary skorundan devam edelim.

rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

# Frequencyi de aynı şekilde çalıştıralım. (Hata alacağız.)

rfm["frequency_score"] = pd.qcut(rfm["frequency"], 5, labels=[1, 2, 3, 4, 5])

# Karşımıza çıkan hata : Oluşturulan aralıklarda unique değerler yer almamaktadır. Yani o kadar fazla tekrar eden bir frekans var ki küçükten büyüğe sıralandığında çeyrek değerlere düşen değerler aynı olmuş. Bu problemi çözmek için rank metodunu kullanıyoruz. (İlk gördüğünü ilk sınıfa ata bilgisini veriyoruz.)

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels = [1, 2, 3, 4, 5])

# Şimdiki aşamada r ve f değerlerini bir araya getirerek yazmamız gerekmektedir.

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))

rfm.describe().T

# Şampiyon sınıftaki müşteriler kim bakmak için

rfm[rfm["RFM_SCORE"] == "55"]

# Başka bir müşteri sınıfına bakalım

rfm[rfm["RFM_SCORE"] == "11"]