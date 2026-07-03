import akshare as ak
import requests
import json
import configparser


class ETF:
    def __init__(self):
        self.cp = configparser.ConfigParser()
        self.cp.read("config.cfg", encoding="utf8")
        if "ETF" not in self.cp.sections():
            raise Exception("Please add [ETF] section to config.cfg first")
        # {"510300": 2.0, "510100": 1.0}
        self.ETFThreshold = json.loads(self.cp.get('ETF', 'ETFThreshold'))
        self.apiKey = self.cp.get('ETF', 'apiKey')

    def get_info(self):
        df = ak.fund_etf_spot_em()
        # 基金折价率：负值表示溢价，正值表示折价
        # 溢价率 = -折价率
        df = df[df["代码"].isin(self.ETFThreshold.keys())][
            ["代码", "名称", "最新价", "IOPV实时估值", "基金折价率"]].copy()

        res = []
        for _, row in df.iterrows():
            code = row["代码"]
            discount_rt = row["基金折价率"]
            if discount_rt is None or str(discount_rt) == "nan":
                print(f"Fund: {code} 折价率: N/A, skipped")
                continue
            premium_rt = -discount_rt  # 溢价率（正数表示溢价）
            threshold = self.ETFThreshold[code]
            print(f"Fund: {code} {row['名称']} 溢价率: {premium_rt:.2f}% 阈值: {threshold}%")
            # 溢价率小于阈值时推送
            if premium_rt < threshold:
                res.append({
                    "代码": code,
                    "名称": row["名称"],
                    "最新价": str(row["最新价"]),
                    "IOPV估值": str(row["IOPV实时估值"]),
                    "溢价率%": f"{premium_rt:.2f}",
                    "阈值%": str(threshold),
                })
        return res

    def md(self, info):
        if not info:
            return
        res = ["| " + " | ".join(list(info[0])) + " |", "| " + " :---: | " * (len(info[0]) - 1) + " :---: |"]
        res.extend("| " + " | ".join(list(i.values())) + " |" for i in info)
        return "\n".join(res)

    def message(self, key, title, body):
        msg_url = f"https://sctapi.ftqq.com/{key}.send"
        print("Sending to:", msg_url)
        r = requests.post(msg_url, data={"title": title, "desp": body})
        print("Push result:", r.status_code, r.text)

    def main(self):
        info = self.get_info()
        print("Info count:", len(info))
        if info:
            md = self.md(info)
            # title = "ETF: " + ", ".join([f"{item['代码']}-溢价率{item['溢价率%']}%" for item in info])
            title = ", ".join([f"{item['代码']}-溢价率{item['溢价率%']}%" for item in info])
            self.message(
                self.apiKey,
                title,
                md,
            )


if __name__ == "__main__":
    etf = ETF()
    etf.main()