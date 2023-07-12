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

# hangi ürün kaç kere satışa konu olmuştur ?
df["Description"].value_counts().head()

# hangi üründen kaçar tane satılmıştır ?
# aşağıdaki kodda quantityler eksi değerde gözükmektedir. veri ön işleme kısmında bu problem ortadan kaldırılacaktır.

df.groupby("Description").agg({"Quantity": "sum"}).head()

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

# rfm["frequency_score"] = pd.qcut(rfm["frequency"], 5, labels=[1, 2, 3, 4, 5])

# Karşımıza çıkan hata : Oluşturulan aralıklarda unique değerler yer almamaktadır. Yani o kadar fazla tekrar eden bir frekans var ki küçükten büyüğe sıralandığında çeyrek değerlere düşen değerler aynı olmuş. Bu problemi çözmek için rank metodunu kullanıyoruz. (İlk gördüğünü ilk sınıfa ata bilgisini veriyoruz.)

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# Şimdiki aşamada r ve f değerlerini bir araya getirerek yazmamız gerekmektedir.

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))

rfm.describe().T

# Şampiyon sınıftaki müşteriler kim bakmak için

rfm[rfm["RFM_SCORE"] == "55"]

# Başka bir müşteri sınıfına bakalım

rfm[rfm["RFM_SCORE"] == "11"]

# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)

# Nümerik anlamda değerlendirmeler yaptık. Bunların karşısına okunabilirliği artırmak adına bu segmentlerin isimlerini yazabiliriz.

# Bunun için regex kullanacağız. Ancak şu aşamada regexin kendisi konumuzun içinde değil.

# RFM İsimlendirmesi

seg_map = {
    r"[1-2][1-2]": "hibernating",
    r"[1-2][3-4]": "at_Risk",
    r"[1-2]5": "cant_loose",
    r"3[1-2]": "about_to_sleep",
    r"33": "need_attention",
    r"[3-4][4-5]": "loyal_customers",
    r"41": "promising",
    r"51": "new_customers",
    r"[4-5][2-3]": "potential_loyalists",
    r"5[4-5]": "champions"
}

# Çok basit bir kod yazarak diyeceğiz ki yukarıdaki ifade regexi ifade etmektedir.

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

# Segmentleri oluşturduk. Şimdi segmentlerin analizini yapmamız gerekmektedir. Örneğin bu sınıflardaki kişilerin recency ortalamaları nedir ?

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

# need_attention sınıfıyla ilgilenmek istediğimizi düşünelim.

rfm[rfm["segment"] == "need_attention"].head()

# cant_loose a erişmek için:

rfm[rfm["segment"] == "cant_loose"].head()

# new_customers sınıfındakilerin idlerine erişmek istediğimizi düşünelim.

rfm[rfm["segment"] == "new_customers"].index

# yeni müşterilerin idlerini ilgili departmanlara yeni bir dataframele göndermek istediğimizi düşünelim.

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index

# idleri integera çevirelim.

new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)

# İlgili departmana bunu iletmek için excel ya da csv formatına çevirmemiz gereklidir. Çalışmamızı csv haline getirip dışarı çıkaralım.

new_df.to_csv("new_customers.csv")

# rfm çalışmamızı dışarı çıkaralım.

rfm.to_csv("rfm.csv")

# 7. Tüm Sürecin Fonksiyonlaştırılması

def create_rfm(dataframe, csv=False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days,
                                                "Invoice": lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})

    rfm.columns = ["recency", "frequency", "monetary"]
    rfm = rfm[(rfm["monetary"] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                        rfm["frequency_score"].astype(str))

    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r"[1-2][1-2]": "hibernating",
        r"[1-2][3-4]": "at_risk",
        r"[1-2]5": "cant_loose",
        r"3[1-2]": "about_to_sleep",
        r"33": "need_attention",
        r"[3-4][4-5]": "loyal_customers",
        r"41": "promising",
        r"51": "new_customers",
        r"[4-5][2-3]": "potential_loyalists",
        r"5[4-5]": "champions"
    }

    rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

df = df_.copy()

rfm_new = create_rfm(df, csv=True)

# Daha neler yapılabilir ?

# 1.si fonksiyondaki alt özellikler parçalanabilir. Yani bu veri hazırlama, rfm metriklerinin hazırlanması gibi başlıklar için ayrı ayrı fonksiyonlar yazılabilir. Bu fonksiyonlar ayrı ayrı yazıldıktan sonra ara işlemlere müdahale etme şansımız olur. (Bir fonksiyondaki çıktı diğer fonksiyona girdi olacak şekilde.)

# Bu analiz dönem dönem tekrar edilebilir. Örneğin bu analizi yaptıktan belirli bir süre sonra mevzu bahis müşterilerden bazıları artık müşteri olmayabilir. Dolayısıyla buradaki değişimleri gözlemlemek oldukça kritik ve önemlidir. Çünkü takip etme süreci günümüzde şirketler için önemli bir problem oluşturmaktadır.
