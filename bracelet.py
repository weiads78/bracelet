from datetime import datetime
import svgwrite
import math
import pytz

# 预定义常用城市的时区映射
CITY_TIMEZONE_MAP = {
    # 亚洲城市
    "shanghai": "Asia/Shanghai",
    "beijing": "Asia/Shanghai",
    "tokyo": "Asia/Tokyo",
    "singapore": "Asia/Singapore",
    "hong_kong": "Asia/Hong_Kong",
    "seoul": "Asia/Seoul",
    "dubai": "Asia/Dubai",
    "bangkok": "Asia/Bangkok",
    # 欧洲城市
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "rome": "Europe/Rome",
    "madrid": "Europe/Madrid",
    "amsterdam": "Europe/Amsterdam",
    "moscow": "Europe/Moscow",
    # 美洲城市
    "new_york": "America/New_York",
    "los_angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "toronto": "America/Toronto",
    "vancouver": "America/Vancouver",
    "sao_paulo": "America/Sao_Paulo",
    # 大洋洲城市
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "auckland": "Pacific/Auckland",
    # 非洲城市
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "lagos": "Africa/Lagos",
}


def get_timezone(city_name):
    """通过城市名获取时区信息"""
    city_key = city_name.lower().replace(" ", "_")
    if city_key in CITY_TIMEZONE_MAP:
        return pytz.timezone(CITY_TIMEZONE_MAP[city_key])
    else:
        return None


def print_available_cities():
    """打印所有可用的城市列表"""
    print("\n可用的城市列表：")
    regions = {
        "亚洲": [
            city
            for city in CITY_TIMEZONE_MAP.keys()
            if "Asia" in CITY_TIMEZONE_MAP[city]
        ],
        "欧洲": [
            city
            for city in CITY_TIMEZONE_MAP.keys()
            if "Europe" in CITY_TIMEZONE_MAP[city]
        ],
        "美洲": [
            city
            for city in CITY_TIMEZONE_MAP.keys()
            if "America" in CITY_TIMEZONE_MAP[city]
        ],
        "大洋洲": [
            city
            for city in CITY_TIMEZONE_MAP.keys()
            if "Australia" in CITY_TIMEZONE_MAP[city]
            or "Pacific" in CITY_TIMEZONE_MAP[city]
        ],
        "非洲": [
            city
            for city in CITY_TIMEZONE_MAP.keys()
            if "Africa" in CITY_TIMEZONE_MAP[city]
        ],
    }

    for region, cities in regions.items():
        print(f"\n{region}:")
        print(", ".join(cities).replace("_", " ").title())


def generate_bracelet_svg(tz1, tz2, filename="bracelet.svg"):
    """生成双环时间刻度的 SVG 文件"""
    # 基础参数
    center = (150, 150)  # SVG 中心坐标
    inner_radius = 70  # 内环半径
    outer_radius = 90  # 外环半径

    # 计算时区时差
    now = datetime.now(pytz.UTC)
    time1 = now.astimezone(tz1)
    time2 = now.astimezone(tz2)
    time_diff = (time2.utcoffset() - time1.utcoffset()).total_seconds() / 3600

    dwg = svgwrite.Drawing(filename, size=("300mm", "300mm"), viewBox=("0 0 300 300"))

    # 添加渐变定义
    gradient = dwg.defs.add(dwg.radialGradient(id="background_gradient"))
    gradient.add_stop_color(offset="0%", color="#f0f8ff", opacity=0.8)  # 淡蓝色
    gradient.add_stop_color(offset="100%", color="#e6e6fa", opacity=0.3)  # 淡紫色

    # 添加背景
    dwg.add(
        dwg.circle(center=center, r=outer_radius + 40, fill="url(#background_gradient)")
    )

    # 添加装饰环
    dwg.add(
        dwg.circle(
            center=center,
            r=outer_radius + 2,
            fill="none",
            stroke="#b0c4de",
            stroke_width=0.5,
            opacity=0.6,
        )
    )
    dwg.add(
        dwg.circle(
            center=center,
            r=inner_radius - 2,
            fill="none",
            stroke="#b0c4de",
            stroke_width=0.5,
            opacity=0.6,
        )
    )

    # 绘制双环
    def draw_ring(radius, tz, is_inner=True, hour_offset=0):
        # 绘制24小时刻度
        for hour in range(24):
            # 计算考虑时差后的角度
            adjusted_hour = (hour + hour_offset) % 24
            angle = math.radians(360 * adjusted_hour / 24 - 90)  # -90使0点指向上方
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)

            # 刻度线
            line_length = 8 if is_inner else 12
            line_color = (
                "#4682b4" if hour % 6 == 0 else "#778899"
            )  # 主要刻度使用不同颜色
            line_width = 1.5 if hour % 6 == 0 else 0.8
            line = dwg.line(
                start=(x, y),
                end=(
                    x + line_length * math.cos(angle),
                    y + line_length * math.sin(angle),
                ),
                stroke=line_color,
                stroke_width=line_width,
            )
            dwg.add(line)

            # 小时数字
            text_radius = radius - 15 if is_inner else radius + 20
            tx = center[0] + text_radius * math.cos(angle)
            ty = center[1] + text_radius * math.sin(angle)

            text_color = "#2f4f4f" if hour % 6 == 0 else "#696969"
            text = dwg.text(
                str(hour),
                insert=(tx, ty),
                text_anchor="middle",
                dominant_baseline="central",
                transform=f"rotate({math.degrees(angle)+90} {tx} {ty})",
                font_size="10px",
                fill=text_color,
                font_family="Arial",
            )
            dwg.add(text)

        # 添加时区标签和当前时间
        label = f"{tz.zone.split('/')[-1]} "
        label_color = "#4169e1"
        
        # 根据是内圈还是外圈决定标签位置
        label_offset = radius + 25
        if is_inner:
            label_offset = radius - 35  # 内圈标签向内偏移
            
        dwg.add(dwg.text(
            label,
            insert=(center[0], center[1] - label_offset),
            text_anchor="middle",
            font_size="10px",
            fill=label_color,
            font_family="Arial",
            font_weight="bold"
        ))

        # 添加装饰点
        for i in range(4):
            dot_angle = math.radians(i * 90)
            dot_x = center[0] + (radius + 5) * math.cos(dot_angle)
            dot_y = center[1] + (radius + 5) * math.sin(dot_angle)
            dwg.add(dwg.circle(center=(dot_x, dot_y), r=1, fill="#4682b4", opacity=0.8))

    # 绘制内环（基准时区）和外环（目标时区，需要考虑时差）
    draw_ring(inner_radius, tz1, is_inner=True, hour_offset=0)
    draw_ring(outer_radius, tz2, is_inner=False, hour_offset=int(time_diff))

    # 添加中心点和装饰环
    dwg.add(dwg.circle(center=center, r=4, fill="#4682b4", opacity=0.9))
    dwg.add(dwg.circle(center=center, r=2, fill="#f0f8ff"))

    # 添加时差说明
    time_diff_text = (
        f"时差：{abs(int(time_diff))}小时" if time_diff != 0 else "相同时区"
    )
    dwg.add(
        dwg.text(
            time_diff_text,
            insert=(center[0], center[1] + outer_radius + 40),
            text_anchor="middle",
            font_size="12px",
            fill="#4682b4",
            font_family="Arial",
        )
    )

    dwg.save()
    print(f"文件已生成：{filename}")


# 主程序
if __name__ == "__main__":
    print_available_cities()
    print("\n请从上面的城市列表中选择：")
    city1 = input("请输入您的城市：")
    city2 = input("请输入好友的城市：")

    tz1 = get_timezone(city1)
    tz2 = get_timezone(city2)

    if not tz1 or not tz2:
        print("错误：无法获取时区信息，请检查城市名称是否在支持列表中")
    else:
        generate_bracelet_svg(tz1, tz2)
