import time
import pandas as pd
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rera_scraper.log'),
        logging.StreamHandler()
    ]
)

class ReraScraper:
    def __init__(self):
        self.browser = None
        self.wait = None
        self.output_dir = 'output'
        self.create_output_directory()
        
    def create_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def init_browser(self):
        """Initialize browser with advanced options"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        service = Service(ChromeDriverManager().install())
        self.browser = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.browser, 10)
        
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present and visible"""
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.warning(f"Timeout waiting for element: {value}")
            return None
            
    def get_project_details(self, project_link):
        """Extract detailed project information"""
        try:
            project_link.click()
            time.sleep(2)
            
            details = {
                'RERA Regd. No': 'N/A',
                'Project Name': 'N/A',
                'Promoter Name': 'N/A',
                'Promoter Address': 'N/A',
                'GST No': 'N/A',
                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract basic project info with retry mechanism
            for field, xpath in [
                ('RERA Regd. No', "//label[contains(text(), 'RERA Regd. No')]/following-sibling::div"),
                ('Project Name', "//label[contains(text(), 'Project Name')]/following-sibling::div")
            ]:
                try:
                    element = self.wait_for_element(By.XPATH, xpath)
                    if element:
                        details[field] = element.text.strip()
                except Exception as e:
                    logging.error(f"Error extracting {field}: {str(e)}")
            
            # Extract promoter details
            try:
                promoter_tab = self.wait_for_element(By.XPATH, "//a[contains(text(), 'Promoter Details')]")
                if promoter_tab:
                    promoter_tab.click()
                    time.sleep(2)
                    
                    for field, xpath in [
                        ('Promoter Name', "//label[contains(text(), 'Company Name')]/following-sibling::div"),
                        ('Promoter Address', "//label[contains(text(), 'Registered Office Address')]/following-sibling::div"),
                        ('GST No', "//label[contains(text(), 'GST No')]/following-sibling::div")
                    ]:
                        try:
                            element = self.wait_for_element(By.XPATH, xpath)
                            if element:
                                details[field] = element.text.strip()
                        except Exception as e:
                            logging.error(f"Error extracting {field}: {str(e)}")
            except Exception as e:
                logging.error(f"Error accessing promoter details: {str(e)}")
            
            self.browser.back()
            time.sleep(2)
            return details
            
        except Exception as e:
            logging.error(f"Error processing project: {str(e)}")
            return None
            
    def save_data(self, projects):
        """Save data in multiple formats"""
        if not projects:
            logging.error("No projects data to save")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as CSV
        csv_path = os.path.join(self.output_dir, f'odisha_rera_projects_{timestamp}.csv')
        df = pd.DataFrame(projects)
        df.to_csv(csv_path, index=False)
        logging.info(f"Data saved to CSV: {csv_path}")
        
        # Save as Excel with formatting
        excel_path = os.path.join(self.output_dir, f'odisha_rera_projects_{timestamp}.xlsx')
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Projects')
            workbook = writer.book
            worksheet = writer.sheets['Projects']
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Apply header format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 30)
                
        logging.info(f"Data saved to Excel: {excel_path}")
        
    def run(self):
        """Main execution method"""
        try:
            logging.info("Starting RERA project scraper")
            self.init_browser()
            
            self.browser.get("https://rera.odisha.gov.in/projects/project-list")
            time.sleep(5)
            
            projects = []
            project_links = self.browser.find_elements(By.CSS_SELECTOR, "a.btn.btn-primary")[:6]
            
            for i, link in enumerate(project_links, 1):
                logging.info(f"Processing project {i} of {len(project_links)}")
                project_data = self.get_project_details(link)
                if project_data:
                    projects.append(project_data)
            
            self.save_data(projects)
            logging.info("Scraping completed successfully")
            
        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            
        finally:
            if self.browser:
                self.browser.quit()
                logging.info("Browser closed")

if __name__ == "__main__":
    scraper = ReraScraper()
    scraper.run() 