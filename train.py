from display import Display, FontStyles
from fonts import Fonts
import math
from zeep import Client, Settings
from zeep import xsd
from zeep.plugins import HistoryPlugin

class TrainDeparture(Display):
    SERVICE_WIDTH = 120
    PADDING = 8
    FETCH_INTERVAL = 20
    PAGE_INTERVAL  = 10

    def __init__(self, w, h, px_sep, x, y):
        super().__init__(w, h, px_sep, x, y)
        self.draw_spacers()
        self.init_ldbws_api()
        self.call_pages = []
        self.services   = []
        self.ticks = 20

    def init_ldbws_api(self):
        WSDL_URL = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2021-11-01"
        TOKEN = "your-ldbws-token-here"

        history = HistoryPlugin()
        settings = Settings(strict=False, xsd_ignore_sequence_order=True)
        self.client = Client(wsdl=WSDL_URL, plugins=[history], settings=settings)

        header = xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
            xsd.ComplexType([
                xsd.Element(
                    '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
                    xsd.String()),
            ])
        )
        self.ldb_header = header(TokenValue=TOKEN)

    def draw_spacers(self):
        for i in range(self.w // (self.SERVICE_WIDTH + self.PADDING) + 1):
            self.draw_rect(
                i*(self.SERVICE_WIDTH+self.PADDING),
                0,
                self.PADDING,
                self.h,
            )
            self.draw_rect(
                max(0, i*(self.SERVICE_WIDTH+self.PADDING) - 8),
                34,
                8,
                self.h,
            )

        self.draw_rect(0, 13, self.w, 4)
        self.draw_rect(0, 30, self.w, 4)

        for i in range(self.h // (9 + 3)):
            self.draw_rect(0, 34 + (i+1)*(9 + 3) - 3, self.w, 3)
        self.draw_rect(0, 34 + ((self.h-34) // (9+3))*(9+3), self.w, 9 + 3)

    def fetch_data(self):
        crs = "MAN"

        if self.client == None:
            return
        res = self.client.service.GetDepBoardWithDetails(
            numRows = self.w // self.SERVICE_WIDTH + 1,
            crs = crs,
            _soapheaders = [self.ldb_header],
        )

        old_services = self.services.copy()
        self.services = res.trainServices.service
        i = 0
        while i < len(self.services):
            t = self.services[i]
            
            if i < len(old_services):
                tt = old_services[i]
                if t.serviceID == tt.serviceID:
                    i += 1
                    continue

            if i < len(self.call_pages):
                self.call_pages[i] = [-1, -1]
            else:
                self.call_pages.append([-1, -1])

            i += 1


    def update(self):
        if self.ticks % self.FETCH_INTERVAL == 0:
            self.fetch_data()

        services = self.services

        i = 0
        xx = self.PADDING
        while i < len(services):
            t = services[i]
            
            yy = 0
            # Line 1
            self.print(t.std, xx, yy, self.SERVICE_WIDTH, style=FontStyles.LARG)
            platform_txt = f"Plat {t.platform if t.platform else '-'}"
            platform_txt_len = self.get_text_length(platform_txt, style=FontStyles.LARG)
            self.print(
                platform_txt,
                xx + self.SERVICE_WIDTH - platform_txt_len,
                yy,
                platform_txt_len,
                style=FontStyles.LARG,
            )
            yy += 17

            # Line 2
            self.print(
                t.destination.location[0].locationName,
                xx,
                yy,
                self.SERVICE_WIDTH,
                style=FontStyles.LARG,
            )
            yy += 17

            # Line 3
            calling_points = t.subsequentCallingPoints.callingPointList[0].callingPoint

            self.print("Calling at:", xx, yy, self.SERVICE_WIDTH, style=FontStyles.NARR)

            call_page_size = (self.h - yy) // 12 - 3
            total_call_pages = math.ceil(len(calling_points) / call_page_size)
            if total_call_pages != self.call_pages[i][1]:
                self.call_pages[i][0] = total_call_pages
                self.call_pages[i][1] = total_call_pages

            # Change Page
            if self.ticks % self.PAGE_INTERVAL == 0:
                if self.call_pages[i][0] < self.call_pages[i][1]:
                    self.call_pages[i][0] += 1
                else:
                    self.call_pages[i][0] = 1

            cur_page = self.call_pages[i][0]
            tot_pages = self.call_pages[i][1]
            if cur_page == -1 or total_call_pages == -1:
                page_txt = f"Page - of -"
            else:
                page_txt = f"Page {cur_page} of {tot_pages}"

            txt_len = self.get_text_length(page_txt, style=FontStyles.NARR)
            self.print(
                page_txt,
                xx + self.SERVICE_WIDTH - txt_len,
                yy,
                txt_len,
                style=FontStyles.NARR,
            )
            yy += 12

            # Calling Points Lines
            for j in range(call_page_size * (cur_page - 1), call_page_size * (cur_page)):
                if j < len(calling_points):
                    c = calling_points[j].locationName
                else:
                    c = " "

                self.print(c, xx, yy, self.SERVICE_WIDTH - 8, style=FontStyles.REGU)
                yy += 12

            # Line 4
            self.print(f"Formed of {t.length} coaches", xx, yy, self.SERVICE_WIDTH - 8, style=FontStyles.REGU)
            yy += 12

            # Line 4
            self.print(f"{t.operator}", xx, yy, self.SERVICE_WIDTH - 8, style=FontStyles.BOLD)
            yy += 12

            i += 1
            xx += self.SERVICE_WIDTH + self.PADDING

        self.ticks += 1
        if self.ticks > 100000:
            self.ticks = 0
