from display import Display, FontStyles
from fonts import Fonts
from zeep import Client, Settings
from zeep import xsd
from zeep.plugins import HistoryPlugin

class TrainDeparture(Display):
    SERVICE_WIDTH = 120
    PADDING = 8

    def __init__(self, w, h, px_sep, x, y):
        super().__init__(w, h, px_sep, x, y)
        self.draw_spacers()
        self.init_ldbws_api()

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

    def update(self):
        crs = "MAN"

        if self.client == None:
            return
        res = self.client.service.GetDepBoardWithDetails(
            numRows = self.w // self.SERVICE_WIDTH + 1,
            crs = crs,
            _soapheaders = [self.ldb_header],
        )

        services = res.trainServices.service
        i = 0
        xx = self.PADDING
        while i < len(services):
            t = services[i]

            # Line 1
            self.print(t.std, xx, 0, self.SERVICE_WIDTH, style=FontStyles.LARG)
            platform_txt = f"Plat {t.platform if t.platform else '-'}"
            platform_txt_len = self.get_text_length(platform_txt, style=FontStyles.LARG)
            self.print(
                platform_txt,
                xx + self.SERVICE_WIDTH - platform_txt_len,
                0,
                platform_txt_len,
                style=FontStyles.LARG,
            )

            # Line 2
            self.print(
                t.destination.location[0].locationName,
                xx,
                17,
                self.SERVICE_WIDTH,
                style=FontStyles.LARG,
            )

            # Line 3
            self.print("Calling at:", xx, 34, self.SERVICE_WIDTH, style=FontStyles.NARR)
            page_txt = f"Page - of -"
            txt_len = self.get_text_length(page_txt, style=FontStyles.NARR)
            self.print(
                page_txt,
                xx + self.SERVICE_WIDTH - txt_len,
                34,
                txt_len,
                style=FontStyles.NARR,
            )

            i += 1
            xx += self.SERVICE_WIDTH + self.PADDING


