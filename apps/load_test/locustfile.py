"""
==========================================================================
 LOAD TEST — Locust Performance Test Script untuk SERPTECH/SIMS ERP
==========================================================================
 Digunakan untuk test performa aplikasi dengan concurrent user.
 
 Cara Pakai:
 1. pip install locust
 2. Pastikan aplikasi Django berjalan (python manage.py runserver)
 3. Jalankan: locust -f apps/load_test/locustfile.py --host=http://127.0.0.1:8000
 4. Buka http://localhost:8089 untuk dashboard Locust
 5. Atur jumlah user, spawn rate, dan mulai test

 Test Scenarios:
 - Login (4 users per detik)
 - Dashboard loading (berat — ApexCharts + DataTable)
 - POS checkout (cepat — kritis)
 - DataTable list views (pagination + filter)
 - Export Excel/PDF (berat — data processing)
 - Purchase Order create (medium)
==========================================================================
"""
import json
import random
import string
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask


class ERPUser(HttpUser):
    """
    Simulasi user ERP dengan workflow realistis:
    1. Login → 2. Dashboard → 3. Browse list → 4. Create transaction
    """
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login sebelum memulai test"""
        self.login()
    
    def login(self):
        """Login user ke aplikasi"""
        response = self.client.get("/accounts/login/")
        if response.status_code == 200:
            csrf_token = response.cookies.get("csrftoken", "")
            login_data = {
                "username": "admin",
                "password": "testpass123",
                "csrfmiddlewaretoken": csrf_token,
            }
            self.client.post(
                "/accounts/login/",
                data=login_data,
                headers={"Referer": self.host + "/accounts/login/"},
            )
    
    @task(weight=3)
    def load_dashboard(self):
        """Load dashboard — heavy: ApexCharts + stats"""
        self.client.get("/", name="Dashboard")
    
    @task(weight=2)
    def load_produk_list(self):
        """Load daftar produk dengan DataTable"""
        self.client.get("/produk/", name="Produk List")
    
    @task(weight=2)
    def load_po_list(self):
        """Load daftar purchase order"""
        self.client.get("/pembelian/po/", name="PO List")
    
    @task(weight=2)
    def load_so_list(self):
        """Load daftar sales order"""
        self.client.get("/penjualan/so/", name="SO List")
    
    @task(weight=1)
    def load_pos_list(self):
        """Load daftar POS transactions"""
        self.client.get("/pos/", name="POS List")
    
    @task(weight=1)
    def load_biaya_list(self):
        """Load daftar biaya"""
        self.client.get("/biaya/", name="Biaya List")
    
    @task(weight=1)
    def load_akuntansi(self):
        """Load dashboard akuntansi — heavy"""
        self.client.get("/akuntansi/", name="Dashboard Akuntansi")
    
    @task(weight=1)
    def load_jurnal_list(self):
        """Load daftar jurnal entry"""
        self.client.get("/akuntansi/jurnal/", name="Jurnal List")
    
    @task(weight=1)
    def load_kas_bank(self):
        """Load kas & bank dashboard"""
        self.client.get("/kas-bank/", name="Kas Bank")
    
    @task(weight=1)
    def load_piutang_list(self):
        """Load daftar piutang"""
        self.client.get("/piutang/", name="Piutang List")
    
    @task(weight=1)
    def load_hutang_list(self):
        """Load daftar hutang"""
        self.client.get("/hutang/", name="Hutang List")
    
    @task(weight=1)
    def load_trial_balance(self):
        """Load trial balance"""
        self.client.get("/akuntansi/neraca-saldo/", name="Trial Balance")
    
    @task(weight=1)
    def load_laporan_keuangan(self):
        """Load laporan keuangan"""
        self.client.get("/laporan/keuangan/", name="Laporan Keuangan")
    
    @task(weight=1)
    def export_excel(self):
        """Simulasi export Excel"""
        self.client.get("/produk/?export=excel", name="Export Excel")
    
    @task(weight=1)
    def export_pdf(self):
        """Simulasi export PDF"""
        self.client.get("/produk/?export=pdf", name="Export PDF")


class POSFlowUser(HttpUser):
    """Simulasi user yang melakukan checkout POS"""
    
    wait_time = between(0.5, 2)
    
    def on_start(self):
        self.login()
    
    def login(self):
        response = self.client.get("/accounts/login/")
        if response.status_code == 200:
            csrf_token = response.cookies.get("csrftoken", "")
            self.client.post(
                "/accounts/login/",
                data={
                    "username": "admin",
                    "password": "testpass123",
                    "csrfmiddlewaretoken": csrf_token,
                },
                headers={"Referer": self.host + "/accounts/login/"},
            )
    
    @task(weight=5)
    def load_pos_page(self):
        """Load halaman POS"""
        self.client.get("/pos/", name="POS Page")
    
    @task(weight=3)
    def create_pos_transaction(self):
        """Simulasi pembuatan POS transaction"""
        self.client.get("/pos/tambah/", name="POS Create")
    
    @task(weight=2)
    def pos_checkout(self):
        """Simulasi checkout (POST request)"""
        # Note: ini membutuhkan data valid
        data = {
            "customer": 1,
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "1",
            "items-MAX_NUM_FORMS": "100",
            "items-0-produk": 1,
            "items-0-quantity": 1,
            "items-0-harga": 7000000,
            "metode_pembayaran": "cash",
            "status": "paid",
        }
        self.client.post("/pos/tambah/", data=data, name="POS Checkout")


class AccountingFlowUser(HttpUser):
    """Simulasi user yang melakukan alur akuntansi"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        self.login()
    
    def login(self):
        response = self.client.get("/accounts/login/")
        if response.status_code == 200:
            csrf_token = response.cookies.get("csrftoken", "")
            self.client.post(
                "/accounts/login/",
                data={
                    "username": "admin",
                    "password": "testpass123",
                    "csrfmiddlewaretoken": csrf_token,
                },
                headers={"Referer": self.host + "/accounts/login/"},
            )
    
    @task(weight=3)
    def load_dashboard(self):
        self.client.get("/", name="Dashboard")
    
    @task(weight=2)
    def load_akuntansi_dashboard(self):
        self.client.get("/akuntansi/", name="Akuntansi Dashboard")
    
    @task(weight=2)
    def load_laba_rugi(self):
        self.client.get("/akuntansi/laba-rugi/", name="Laba Rugi")
    
    @task(weight=2)
    def load_neraca(self):
        self.client.get("/akuntansi/neraca/", name="Neraca")
    
    @task(weight=1)
    def load_rekonsiliasi(self):
        self.client.get("/akuntansi/rekonsiliasi-keuangan/", name="Rekonsiliasi")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Init: print configurasi test
    """
    print("\n" + "=" * 60)
    print("  LOAD TEST — SERPTECH/SIMS ERP")
    print("  Target:", environment.host)
    print("  Users:", environment.runner.target_user_count if environment.runner else "N/A")
    print("  Spawn rate:", environment.runner.spawn_rate if environment.runner else "N/A")
    print("=" * 60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Summary setelah test selesai
    """
    print("\n" + "=" * 60)
    print("  LOAD TEST COMPLETED")
    print("  Total requests:", environment.stats.total.num_requests)
    print("  Failures:", environment.stats.total.num_failures)
    print("  Avg response time:", round(environment.stats.total.avg_response_time, 2), "ms")
    print("  P95 response time:", round(environment.stats.total.get_response_time_percentile(0.95), 2), "ms")
    print("=" * 60 + "\n")


"""
==========================================================================
 LOAD TEST CONFIGURATION (jalankan via command line)

 # Basic test — 10 user, spawn 2 per detik
 locust -f apps/load_test/locustfile.py --host=http://127.0.0.1:8006

 # Medium test — 25 user
 locust -f apps/load_test/locustfile.py --host=http://127.0.0.1:8006 --users 25 --spawn-rate 5

 # Heavy test — 50 user
 locust -f apps/load_test/locustfile.py --host=http://127.0.0.1:8006 --users 50 --spawn-rate 10 --run-time 300s

 # Headless mode — untuk CI/CD
 locust -f apps/load_test/locustfile.py --host=http://127.0.0.1:8006 \
     --users 30 --spawn-rate 5 --run-time 120s --headless \
     --html=load_test_report.html --csv=load_test_results

 # Test specific user class
 locust -f apps/load_test/locustfile.py --host=http://127.0.0.1:8006 \
     POSFlowUser ERPUser AccountingFlowUser

 RECOMMENDED TARGETS:
 - Response time < 500ms untuk list views
 - Response time < 1000ms untuk dashboard
 - Response time < 2000ms untuk export/PDF
 - Error rate < 1%
 - RPS (Requests Per Second) > 10 per user
==========================================================================
"""