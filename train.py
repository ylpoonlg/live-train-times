from config import CLK_FREQ, parser
from display import Display, FontStyles
import math
import pygame
import threading
from gtts import gTTS
from playsound import playsound
from zeep import Client, Settings
from zeep import xsd
from zeep.plugins import HistoryPlugin

class TrainDeparture(Display):
    SERVICE_WIDTH = 130
    PADDING = 8

    FETCH_INTERVAL    = 10 * CLK_FREQ
    PAGE_INTERVAL     = 5 * CLK_FREQ
    ANNOUNCE_INTERVAL = 120 * CLK_FREQ

    def __init__(self, w, h, px_sep, x, y, crs = ""):
        super().__init__(w, h, px_sep, x, y)
        self.draw_spacers()
        self.init_ldbws_api()
        self.call_pages = []
        self.services   = []
        self.ticks = 0

        parser.add_argument("--crs", type=str, help="Station CRS Code", default="MAN")
        args, _ = parser.parse_known_args()
        if crs == "":
            self.crs = args.crs
        else:
            self.crs = crs

    def init_ldbws_api(self):
        WSDL_URL = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2021-11-01"
        TOKEN = "your-ldbws-token-here"

        history = HistoryPlugin()
        settings = Settings(strict=False, xsd_ignore_sequence_order=True)

        try:
            self.client = Client(wsdl=WSDL_URL, plugins=[history], settings=settings)
        except:
            print("Failed to connect to SOAP client. Check Network Connection.")
            self.client = None

        header = xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
            xsd.ComplexType([
                xsd.Element(
                    '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
                    xsd.String()),
            ])
        )
        self.ldb_header = header(TokenValue=TOKEN)

    def draw_decorations(self, screen):
        font = pygame.font.SysFont("arial", 36)
        img = font.render("Departures", True, (200, 200, 200))
        screen.blit(img, (50, 30))

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
        if self.client == None:
            return
        res = self.client.service.GetDepBoardWithDetails(
            numRows = self.w // self.SERVICE_WIDTH + 1,
            crs = self.crs,
            _soapheaders = [self.ldb_header],
        )

        old_services = self.services.copy()
        if res.trainServices != None:
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

    def announce(self, msg):
        try:
            tts = gTTS(msg, lang="en-gb")
            tts.save("./annc.mp3")
            playsound("./annc.mp3", False)
        except:
            print("=> Announcement not available")

    def update(self):
        if self.ticks % self.FETCH_INTERVAL == 0:
            self.fetch_data()

        services = self.services

        i = 0
        xx = self.PADDING
        annc_text = []
        while i < len(services):
            t = services[i]
            t_dest = t.destination.location[0].locationName

            annc_t = ""
            
            yy = 0
            # Line 1
            self.print(t.std, xx, yy, self.SERVICE_WIDTH, style=FontStyles.LARG, ticks=self.ticks)
            platform_txt = f"Plat {t.platform if t.platform else '-'}"
            if self.ticks % self.PAGE_INTERVAL < self.PAGE_INTERVAL // 2:
                if t.etd == "Delayed":
                    platform_txt = "Delayed"
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
                t_dest,
                xx,
                yy,
                self.SERVICE_WIDTH,
                style=FontStyles.LARG,
                ticks=self.ticks,
            )
            yy += 17

            # Line 3
            END_LINE_INDENT = 8
            calling_points = []
            if t.subsequentCallingPoints != None:
                if len(t.subsequentCallingPoints.callingPointList) > 0:
                    calling_points = t.subsequentCallingPoints.callingPointList[0].callingPoint
            self.print("Calling at:", xx, yy, self.SERVICE_WIDTH - END_LINE_INDENT, style=FontStyles.NARR, ticks=self.ticks)
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
                xx + self.SERVICE_WIDTH - END_LINE_INDENT - txt_len,
                yy,
                txt_len,
                style=FontStyles.NARR,
                ticks=self.ticks
            )
            yy += 12

            # Calling Points Lines
            for j in range(call_page_size * (cur_page - 1), call_page_size * (cur_page)):
                if j < len(calling_points):
                    c = calling_points[j].locationName
                else:
                    c = " "
                self.print(c, xx, yy, self.SERVICE_WIDTH - END_LINE_INDENT, style=FontStyles.REGU, ticks=self.ticks)
                yy += 12

            # Line 4
            if t.length != None:
                self.print(f"Formed of {t.length} coaches", xx, yy, self.SERVICE_WIDTH - END_LINE_INDENT, style=FontStyles.REGU, ticks=self.ticks)
            else:
                self.print("", xx, yy, self.SERVICE_WIDTH - END_LINE_INDENT, style=FontStyles.REGU, ticks=self.ticks)
            yy += 12

            # Line 4
            self.print(f"{t.operator}", xx, yy, self.SERVICE_WIDTH - END_LINE_INDENT, style=FontStyles.BOLD, ticks=self.ticks)
            yy += 12

            i += 1
            xx += self.SERVICE_WIDTH + self.PADDING


            # Announcement Text
            do_annc = True
            try:
                if t.platform is None:
                    raise AssertionError
                std_hh, std_mm = t.std.split(":")
                annc_t += f"Platform {t.platform}. for the {std_hh} {std_mm} {t.operator} service. to. {t_dest}. "
                annc_t += "Calling at. "
                for j in range(len(calling_points)):
                    annc_t += calling_points[j].locationName + ". "
                if t.length != None:
                    annc_t += f"This train is formed of {t.length} coaches. "
            except:
                do_annc = False

            if do_annc:
                annc_text.append(annc_t)

        btp_msg = """If you see something that doesn't look right, speak to staff,
        or text the British Transport Police, on, 6 1 O 1 6.. We'll sort it..
        See it. Say it. Sorted."""
        if self.ticks % self.ANNOUNCE_INTERVAL == 0:
            if len(annc_text) > 0:
                threading.Thread(target=self.announce, args=(". ".join(annc_text),)).start()
            else:
                threading.Thread(
                    target=self.announce,
                    args=(btp_msg,),
                ).start()
        elif self.ticks % (2 * self.ANNOUNCE_INTERVAL) == self.ANNOUNCE_INTERVAL // 2:
            threading.Thread(
                target=self.announce,
                args=(btp_msg,),
            ).start()

        # Increment ticks count
        self.ticks += 1
        if self.ticks > 100000:
            self.ticks = 0

    def abbrv(self, text) -> str:
        WORD_ABBRV = {
            "International": "Intl.",
        }
        FULL_ABBRV = {
            "Great Western Railway": "GWR",
        }

        result = []
        words = text.split(" ")
        for w in words:
            result.append(WORD_ABBRV.get(w, w))
        text =  " ".join(result)

        for k, v in FULL_ABBRV.items():
            text = text.replace(k, v)

        return text

