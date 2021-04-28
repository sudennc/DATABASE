**CASE1**

1.	SUNUCU : CENTOS 7    192.168.98.136
2.	SUNUCU : CENTOS 7    192.168.98.131

1)	**Transparent Huge Pages(THP) kapatılır.Çünkü çoğu Linux işletim sisteminde varsayılan olarak etkinleştirilen bir bellek yönetim sistemidir. Couchbase Sunucusunun Linux'ta düzgün çalışması için THP devre dışı bırakılmalıdır.**

- 1.1)	Root kullanıcısına geçilir.

- 1.2)	Thp’nin kapatılacağı dosyaya gidilir.

	`[root@couchbase1 sudenurcelen]# vi /etc/init.d/disable-thp  `

- 1.3)	 Aşağıdaki script dosya içine yapıştırılır.

		#!/bin/bash
		### BEGIN INIT INFO
		# Provides:          disable-thp
		# Required-Start:    $local_fs
		# Required-Stop:
		# X-Start-Before:    couchbase-server
		# Default-Start:     2 3 4 5
		# Default-Stop:      0 1 6
		# Short-Description: Disable THP
		# Description:       Disables transparent huge pages (THP) on boot, to improve
		#                    Couchbase performance.
		### END INIT INFO

		case $1 in
 		 start)
		    if [ -d /sys/kernel/mm/transparent_hugepage ]; then
		      thp_path=/sys/kernel/mm/transparent_hugepage
		    elif [ -d /sys/kernel/mm/redhat_transparent_hugepage ]; then
		      thp_path=/sys/kernel/mm/redhat_transparent_hugepage
		    else
		      return 0
		    fi

		    echo 'never' > ${thp_path}/enabled
		    echo 'never' > ${thp_path}/defrag

		    re='^[0-1]+$'
		    if [[ $(cat ${thp_path}/khugepaged/defrag) =~ $re ]]
		    then
		      # RHEL 7
		      echo 0  > ${thp_path}/khugepaged/defrag
		    else
		      # RHEL 6
		      echo 'no' > ${thp_path}/khugepaged/defrag
		    fi

		    unset re
		    unset thp_path
		    ;;
		esac


- 1.4)	Dosya kaydedilir ve executeble duruma getirilir.

  `[root@couchbase1 sudenurcelen]# chmod 755 /etc/init.d/disable-thp`

- 1.5)	Servis başlatılır.

 `[root@couchbase1 sudenurcelen]# service disable-thp start`

2)	**Swappiness kapatılır.**

- 2.1) Swappiness değeri kontrol edilir. Sonuç 0 olmalıdır. Çünkü Linux'ta, çekirdeğin swappiness, sistemin RAM kullanımına bağlı olarak fiziksel bellekteki sayfaları değiştirme olasılığının ne kadar olduğunu gösterir. En iyi Couchbase Sunucu performansını elde etmek için çoğu Linux sisteminde swappiness 1 veya 0 olarak ayarlanmalıdır.

 `[root@couchbase1 sudenurcelen]# cat /proc/sys/vm/swappiness
30`

- 2.2) Swappiness 0 yapılır.

 `[root@couchbase1 sudenurcelen]# sudo sysctl vm.swappiness=0
vm.swappiness = 0`

- 2.3 Tekrardan kontrol edilir.

 `[root@couchbase1 sudenurcelen]# cat /proc/sys/vm/swappiness
0`

**3)	Uzak makineden bağlanabilmek için firewall kapatılır.**

![3](https://user-images.githubusercontent.com/28504151/116298800-94a1b480-a7a5-11eb-92c1-4664c4e8b065.png)



**4)	Couchbase için grup ve kullanıcı oluşturulur.**

 `[root@couchbase1 sudenurcelen]# groupadd -g 909 nosql `  
 `[root@couchbase1 sudenurcelen]# useradd -g nosql -m -s /bin/bash -d /home/couchbase -c "couchbase server" -u 909 couchbase`
`[root@couchbase1 sudenurcelen]# passwd couchbase   -- trendyolbc1+`

**5)	Ulimit değeri ayarlanır.**

 `[root@couchbase1 sudenurcelen]# vi /etc/security/limits.conf  `
- 5.1) Aşağıdaki değerler limits.conf dosyasına girilir.

		couchbase     soft  nofile  51200
		couchbase     hard  nofile  51200

**6)	Couchbase klasörü ve verilerin tutulacağı klasör oluşturulur.**

 `[root@couchbase1 sudenurcelen]# mkdir /couchbase`
 
 `[root@couchbase1 sudenurcelen]# chown couchbase:nosql /couchbase/`
 
- 6.1)  /setupfile bizim kurulum dosyasının duracağı yer
- 
 `[root@couchbase1 sudenurcelen]# mkdir /setupfile`
 
 -6.2) /setupfile dizinine erişim yetkisi düzenlenir. 
 
 `[root@couchbase1 sudenurcelen]# chown couchbase:nosql /setupfile/`
 
- 6.3) Verilerimizin bulunacağı klasörü oluştururuz.
- 
 `[root@couchbase1 sudenurcelen]# mkdir /data01`
 
 `[root@couchbase1 sudenurcelen]# chown couchbase:nosql /data01`
**7)	Couchbase kullanıcısına geçilir. **

**8)	Kurulum dosyası ve installer /setupfile klasörüne atılır. Ardından installer için executable yetkisi verilir.**

 `chmod u+x ./cb-non-package-installer`

**9)	Installer ile kurulum yapılır.**

`./cb-non-package-installer --install --install-location /couchbase --package couchbase-server-enterprise-6.6.2-centos7.x86_64.rpm`

**10)	Couchbase servisinin başlatılacağı dizine gidilir ve couchbase başlatılır.**

 `cd /couchbase/opt/couchbase`
 
 `./bin/couchbase-server \-- -noinput -detached`
 
 -10.1) Eğer bu servisi kapatmak istersek bu komutu gireriz.

 `Kapatma : ./bin/couchbase-server -k`
 
 ![10](https://user-images.githubusercontent.com/28504151/116298953-c3b82600-a7a5-11eb-9ad7-dd79748a22d5.png)

**11)	Aynı işlemler diğer sunucular için yapılır.**

**12)	Tarayıcıdan 8091 portu üzerinden bağlanabiliriz.** 

![12](https://user-images.githubusercontent.com/28504151/116299012-d6325f80-a7a5-11eb-9bb2-34ee42e53de5.png)

**13)	İlk sunucu için Setup New Cluster seçilir ve gerekli bilgiler girilir.Cluster name,  Disk Path, sunucuda kullanılacak servisler vb. bu aşamada seçilir.**

![13](https://user-images.githubusercontent.com/28504151/116299107-f2ce9780-a7a5-11eb-8e0d-6fa7ba1aadde.png)

![131](https://user-images.githubusercontent.com/28504151/116299124-f6621e80-a7a5-11eb-86bc-1f7f2dc0aff0.png)

![132](https://user-images.githubusercontent.com/28504151/116299132-f8c47880-a7a5-11eb-9a1f-6b1f5d90b8e5.png)

**14)	Varolan Cluster’a bağlanmak için ‘Join Existing Cluster’ seçeneği seçilir. Ardından gerekli bilgiler girilir**. 

![14](https://user-images.githubusercontent.com/28504151/116299174-07129480-a7a6-11eb-9de3-2c01d0a2c8b4.png)

**15)	Rebalance işlemi başlatılır.**

![15](https://user-images.githubusercontent.com/28504151/116299234-17c30a80-a7a6-11eb-97b1-653b402014ca.png)

![151](https://user-images.githubusercontent.com/28504151/116299245-1abdfb00-a7a6-11eb-8b3a-0035fd137297.png)


**CASE2**

1) Önce sunucumuza Python yükleriz. 

`sudo yum install gcc gcc-c++ python3-devel python3-pip cmake`

2) Python SDK yüklenir.

`python3 -m pip install couchbase`

3) Couchbase, kaynaklara erişimi kontrol etmek için Rol Tabanlı Erişim Kontrolü (RBAC) kullanır.Couchbase Sunucumuzun kurulumu sırasında oluşturulan Full Admin rolünü kullanarak Couchbase'e bağlanıyoruz.

`from couchbase.cluster import Cluster, ClusterOptions`
`from couchbase_core.cluster import PasswordAuthenticator` 
`from couchbase.cluster import QueryOptions`
`cluster = Cluster('couchbase://localhost', ClusterOptions(
  PasswordAuthenticator('Administrator', 'password')))`

4) Kullanıcı adı ve parolayı içeren bir kimlik doğrulayıcı tanımlanmalı ve ardından Cluster'a aktarılmalıdır.

`cb = cluster.bucket('bucket-name')`

5) Bundan sonra dosyamıza datamıza veri ekleriz.

-- Buradaki veri Couchbase'in kendi örnek verisidir.-- 

`airline = {
  "type": "airline",
  "id": 8091,
  "callsign": "CBS",
  "iata": None,
  "icao": None,
  "name": "Couchbase Airways",
}`

6) Verilerimizi ekledikten sonra Couchbase arayüzümüze geliriz. Bucket'ımızda eklediğimiz veri '1' olarak görünüyor.

![1](https://user-images.githubusercontent.com/28504151/116458319-2fb19180-a86d-11eb-9722-198ecbe1e747.png)

