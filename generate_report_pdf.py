#!/usr/bin/env python3.11
"""
心理测评报告PDF生成器
根据data.js中的数据，为每个测评的每个等级/类型生成精美PDF报告
"""
import json
import os
import re
import sys

# 由于data.js是ES module格式，我们需要手动解析
# 这里直接内嵌核心数据

REPORTS = {
    "resilience": {
        "name": "职场心理韧性评估",
        "levels": {
            "A": {
                "title": "等级A：心理韧性较弱",
                "evaluation": "先深呼吸一下。看到这个结果，你可能会有些失落，甚至觉得"果然如此"——但我想告诉你，你愿意花时间来做这个测评，本身就说明你还没有放弃自己，这份勇气值得被看见。你现在的状态，不是因为你不够好，而是你承受的压力已经远超一个人该扛的分量。",
                "dimension_analysis": [
                    ("情绪调节力（低）", "职场中的负面消息都容易在你心里掀起巨大波澜，而且持续很久。这不是你"太脆弱"，而是你的情绪系统正在超负荷运转，就像一台没有散热器的电脑，容易过热。"),
                    ("抗压恢复力（低）", "一次高强度加班可能需要你花很长时间才能缓过来。你的能量池长期在"负债"状态，每一次新的压力都是在没有充满电的情况下继续消耗。"),
                    ("自我效能感（低）", "你可能常常怀疑自己的价值。它反映的不是"你真的不行"，而是"你太久没有被正向反馈了"。一朵花不被看见，不代表它没有在开。"),
                    ("社会支持利用度（低）", "你可能觉得开口求助是"示弱"。心理学研究反复证明：真正能帮我们走出低谷的，往往来自他人的一句"我懂你"。")
                ],
                "scenes": [
                    "深夜11点加完班回家，躺在床上刷手机，看到同行被AI替代的新闻，心里一沉，翻来覆去睡不着",
                    "周末本想好好休息，脑子里却在反复回放周五会议上被领导质疑的瞬间，两天假期在精神内耗中过去了",
                    "想转行又怕来不及，想留下又看不到上升空间，最后还是一个人在深夜默默焦虑"
                ],
                "actions": [
                    "今晚睡前写下今天完成的三件小事（哪怕是"回复了一封邮件"），用具体事实对抗"我什么都做不好"的声音。每晚3分钟，坚持一周。",
                    "明天上班选一个你信任的同事，午休时说一句："最近有点累，你呢？"——你不需要倾诉完整的故事，只需要打开那扇门。",
                    "本周末花30分钟做一个"能量盘点"：左边写"正在消耗我的事"，右边写"给我力量的事"。然后下周在右边那一列里，多做一件事。"
                ],
                "knowledge": "3I模型：心理学家Grotberg发现，心理韧性由三个"I"支撑——I Have（我拥有的外部支持）、I Am（我的内在力量）、I Can（我能做什么）。当你觉得扛不住的时候，不是三个"I"都不存在了，而是你可能暂时忘记了它们。",
                "counselor_note": "你现在所处的状态，不叫"软弱"，叫"扛了太久"。一棵树在风暴中弯了腰，不是树的问题，是风太大了。请允许自己不那么坚强，允许自己需要帮助——这恰恰是最勇敢的选择。"
            },
            "B": {
                "title": "等级B：心理韧性一般",
                "evaluation": "你好呀，你可能既不意外也不慌张——因为你心里其实清楚，自己有些地方做得还行，有些地方确实还在"硬撑"。好消息是，你已经具备了基础，只需要在关键点上精准发力。",
                "dimension_analysis": [
                    ("情绪调节力（中等）", "日常的小摩擦你能处理，但遇到"大场面"你的情绪系统容易超载。你的调节能力像一把伞，小雨没问题，暴雨就撑不住了。"),
                    ("抗压恢复力（中等）", "你有一定的"弹性"，但连续高压会让你明显感到精力断崖式下降。你的恢复像手机充电——如果一直边充边放，电量就会越来越低。"),
                    ("自我效能感（中等）", "你对自己的能力有基本信心，但这份信心不太稳定——顺利时觉得自己还行，受挫时容易全盘否定。不是能力不够，而是"自我确认"的方式太依赖外部反馈了。"),
                    ("社会支持利用度（中等）", "你身边其实有人可以求助，但你不是每次都会用。你可能觉得"小事不好意思麻烦别人"，结果小事攒成了大事。")
                ],
                "scenes": [
                    "同样是加班，有时你能自我调节，有时却会突然崩溃——可能只是看到一条"35岁裁员"的帖子",
                    "你有自己的减压方式，但最近发现效果在递减——跑完步回来，焦虑还在原地等你",
                    "你在朋友面前是"靠谱的那个人"，但你很少把自己的脆弱展示出来"
                ],
                "actions": [
                    "找一个"情绪触发点"，提前准备应对方案。给自己写一条"情绪急救短语"，比如："这句话否定的是方案，不是我这个人。"",
                    "本周主动发起一次"非工作社交"，约一个信任的朋友吃个饭。研究显示，哪怕只是轻松的社交互动，也能显著提升抗压能力。",
                    "给自己设置一个"精力红线"：连续加班超过3天时，第4天必须有一个"最低保护动作"——哪怕只是准时下班后散步20分钟。"
                ],
                "knowledge": "成长型思维（Growth Mindset）：斯坦福大学Carol Dweck发现，"固定型思维"觉得失败=我不行，"成长型思维"觉得失败=我在学。试着把"我不行"改成"我还没学会"，这个切换会让大脑从恐慌模式切换到学习模式。",
                "counselor_note": "你不是不够好，你只是还在找那个最适合自己的节奏。就像跑马拉松，前半程不稳不代表跑不到终点——调整呼吸，找到自己的配速，你会越跑越稳的。"
            },
            "C": {
                "title": "等级C：心理韧性良好",
                "evaluation": "你已经历练出了一套自己的"生存系统"，大部分时候都能稳住自己。不过，"良好"和"强韧"之间还有一段距离——那些偶尔冒出来的焦虑，说明你的系统还有可以优化的空间。",
                "dimension_analysis": [
                    ("情绪调节力（良好）", "大部分时候能快速从负面情绪中抽离，但可能有某些"特定触发器"——涉及年龄焦虑或被比较的场景——依然能精准戳到你。"),
                    ("抗压恢复力（良好）", "恢复速度不错，但可能存在"隐性透支"——身体恢复了，心理的疲劳还在累积。就像信用卡，看起来额度还够，但欠款在慢慢增长。"),
                    ("自我效能感（良好）", "信心较稳定，但可能更多建立在"过往经验"上而非"内在确信"——面对完全陌生的挑战时，信心可能短暂动摇。"),
                    ("社会支持利用度（良好）", "你知道关键时刻找人帮忙，但可能更多在"使用"支持而不是"维护"支持——就像一笔存款，只取不存，迟早会见底。")
                ],
                "scenes": [
                    "每隔一段时间就会有一个"低电量日"——不是哪件事触发的，就是突然觉得"好累"",
                    "你能处理好领导的不合理要求，但偶尔夜深人静时会想："我为什么要一直这么懂事？"",
                    "你有靠谱的朋友圈，但你自己几乎从不主动说"我最近不太好""
                ],
                "actions": [
                    "做"恢复质量"检查：你平时的休息是真的在恢复，还是只是"换了一种消耗"？试试15分钟正念呼吸或什么都不做就坐着发呆。",
                    "主动对一个人"示一次弱"：说一句"最近有点累"，你会发现心里某个角落会松一口气。",
                    "做"两年后的我"规划：两年后你想成为什么样的人？让韧性与方向对齐，不再只是"扛住"，而是"有目的地前进"。"
                ],
                "knowledge": "心理韧性的"波浪模型"：韧性不是一条直线上升的曲线，而是呈波浪形——稳定→被冲击→波动→重新稳定。关键不是避免波动，而是在每次波动中缩短恢复时间。",
                "counselor_note": "你已经很棒了，不是客气话。接下来的路，不只是"扛住"，更是"活出来"——让韧性成为你选择生活的底气，而不只是应对压力的盔甲。"
            },
            "D": {
                "title": "等级D：心理韧性强韧",
                "evaluation": "你已经走过了不少风雨，练就了一身在风浪中自如穿行的本领。不过，韧性高的人也有自己的"盲区"——你太能扛了，所以可能忽略了一些更深层的需求。",
                "dimension_analysis": [
                    ("情绪调节力（高）", "你能快速识别并调节情绪，但你的高效调节可能有一个隐藏代价——你可能"调得太快了"，没有给情绪足够的停留和消化时间。有些情绪不是用来"解决"的，而是用来"听"的。"),
                    ("抗压恢复力（高）", "恢复能力很强，甚至在压力中能找到动力。但"恢复得快"和"真正恢复"可能是两回事。某些深层疲劳可能被"效率"遮盖了。"),
                    ("自我效能感（高）", "有坚定的信心，但高自我效能感有时会让人"一个人扛所有事"——不是扛不动，而是没意识到有些事不需要自己扛。"),
                    ("社会支持利用度（高）", "有广泛人脉，但你在支持别人方面可能做得比接受支持多得多——你是朋友圈的"精神支柱"，但谁来支撑你呢？")
                ],
                "scenes": [
                    "同事觉得你是"最稳的那个人"，但你自己焦虑的时候反而不好意思跟别人说",
                    "你能在AI冲击中找到新机会，但内心偶尔会冒出一个声音："我能一直这么幸运吗？"",
                    "你帮很多人分析过职业困境，但轮到自己的时候反而犹豫"
                ],
                "actions": [
                    "给自己安排一个"无所事事"的半天——不是休息、不是充电，就是纯粹什么都不做。",
                    "主动找一个人聊一次"你的困惑"——你一直在帮别人出主意，这次换你来倾诉。",
                    "做一个"影响力清单"：写下过去一年你帮助过的3个人、你带来的3个改变。给你的韧性和善意一个"存档"。"
                ],
                "knowledge": "创伤后成长（Post-Traumatic Growth）：心理学家Tedeschi发现，经历过重大压力的人，不仅可能恢复，还可能在五个维度上获得成长——更深厚的关系、更强的自我认知、新的人生可能性、更强的精神力量、对生活的更深欣赏。",
                "counselor_note": "你很强大，但强大不是不需要被照顾。你的韧性是天赋，也是你一砖一瓦建起来的城堡——但城堡里的人也需要阳光和花园。在帮助世界之前，先允许自己被这个世界温柔以待。"
            }
        }
    }
}

def generate_html_report(assessment_key, level_key):
    """生成单个报告的HTML"""
    assessment = REPORTS[assessment_key]
    report = assessment["levels"][level_key]
    
    dim_items = ""
    for i, (dim_title, dim_text) in enumerate(report["dimension_analysis"]):
        colors = ["#D4A574", "#F2C4C4", "#7EC8A0", "#3A4F5C"]
        dim_items += f"""
        <div style="margin-bottom: 20px; padding: 14px 16px; border-left: 3px solid {colors[i]}; background: #FAF3E8; border-radius: 0 8px 8px 0;">
            <div style="font-size: 14px; font-weight: 600; color: #3A4F5C; margin-bottom: 4px;">{dim_title}</div>
            <div style="font-size: 13px; color: #4A6575; line-height: 1.7;">{dim_text}</div>
        </div>"""

    scene_items = ""
    for i, scene in enumerate(report["scenes"]):
        emojis = ["🏠", "💭", "🌙"]
        scene_items += f"""
        <div style="display: flex; gap: 10px; margin-bottom: 10px; padding: 12px; background: #F7F7F7; border-radius: 8px;">
            <span style="font-size: 20px;">{emojis[i]}</span>
            <span style="font-size: 13px; color: #4A6575; line-height: 1.6;">{scene}</span>
        </div>"""

    action_items = ""
    for i, action in enumerate(report["actions"]):
        action_items += f"""
        <div style="display: flex; gap: 12px; margin-bottom: 12px; padding: 14px; background: #FAF3E8; border-radius: 12px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #D4A574; color: white; font-size: 13px; font-weight: 700; flex-shrink: 0;">{i+1}</span>
            <span style="font-size: 13px; color: #3A4F5C; line-height: 1.6;">{action}</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Noto Sans SC', sans-serif; color: #3A4F5C; background: white; padding: 40px 32px; max-width: 560px; margin: 0 auto; }}
</style>
</head>
<body>

<!-- 封面区域 -->
<div style="text-align: center; padding: 40px 0 32px; background: linear-gradient(135deg, #D4A574 0%, #F2C4C4 100%); border-radius: 16px; margin-bottom: 28px; color: white;">
    <div style="font-size: 14px; letter-spacing: 3px; opacity: 0.85; margin-bottom: 12px;">心知·心理测评</div>
    <div style="font-size: 28px; font-weight: 700; margin-bottom: 8px;">职场心理韧性评估</div>
    <div style="font-size: 18px; font-weight: 300; opacity: 0.9;">{report["title"]}</div>
    <div style="font-size: 12px; margin-top: 16px; opacity: 0.7;">深度报告 · 个性化解读</div>
</div>

<!-- 免责声明 -->
<div style="font-size: 11px; color: #B0B0B0; text-align: center; margin-bottom: 24px;">
    本测评仅供参考，不构成专业心理诊断
</div>

<!-- 总体评价 -->
<div style="margin-bottom: 28px;">
    <div style="font-size: 16px; font-weight: 600; color: #3A4F5C; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #FAF3E8;">📋 总体评价</div>
    <div style="font-size: 14px; line-height: 1.8; color: #4A6575;">{report["evaluation"]}</div>
</div>

<!-- 维度深度解读 -->
<div style="margin-bottom: 28px;">
    <div style="font-size: 16px; font-weight: 600; color: #3A4F5C; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #FAF3E8;">🔍 维度深度解读</div>
    {dim_items}
</div>

<!-- 生活场景 -->
<div style="margin-bottom: 28px;">
    <div style="font-size: 16px; font-weight: 600; color: #3A4F5C; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #FAF3E8;">💭 你可能的生活场景</div>
    {scene_items}
</div>

<!-- 改善行动 -->
<div style="margin-bottom: 28px;">
    <div style="font-size: 16px; font-weight: 600; color: #3A4F5C; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #FAF3E8;">🎯 本周3件改善行动</div>
    {action_items}
</div>

<!-- 心理学小知识 -->
<div style="margin-bottom: 28px; padding: 18px; background: linear-gradient(135deg, #FAF3E8 0%, #F8DEDE 100%); border-radius: 12px; border: 1px dashed #E8C9A8;">
    <div style="font-size: 14px; font-weight: 600; color: #C08B5A; margin-bottom: 8px;">📚 心理学小知识</div>
    <div style="font-size: 13px; line-height: 1.7; color: #4A6575;">{report["knowledge"]}</div>
</div>

<!-- 咨询师寄语 -->
<div style="margin-bottom: 28px; padding: 28px 20px; background: linear-gradient(135deg, #D4A574 0%, #F2C4C4 100%); border-radius: 16px; text-align: center; color: white;">
    <div style="font-size: 12px; font-weight: 300; letter-spacing: 2px; opacity: 0.85; margin-bottom: 12px;">咨询师寄语</div>
    <div style="font-size: 16px; font-weight: 300; line-height: 1.8; font-style: italic;">{report["counselor_note"]}</div>
</div>

<!-- 引导 -->
<div style="text-align: center; padding: 24px; border-top: 1px solid #EFEFEF;">
    <div style="font-size: 14px; color: #8C8C8C; margin-bottom: 12px;">如需更深入的个人成长方案</div>
    <div style="display: inline-block; padding: 10px 32px; background: #D4A574; color: white; border-radius: 999px; font-size: 14px; font-weight: 500;">预约1对1咨询</div>
</div>

<!-- 底部 -->
<div style="font-size: 10px; color: #D9D9D9; text-align: center; margin-top: 20px;">
    心知·心理测评 | 仅供参考，不构成专业心理诊断
</div>

</body>
</html>"""
    return html

def generate_all_reports():
    """生成所有报告"""
    output_dir = "/workspace/psyche-assessment/reports"
    os.makedirs(output_dir, exist_ok=True)
    
    for assessment_key, assessment_data in REPORTS.items():
        for level_key, report_data in assessment_data["levels"].items():
            html = generate_html_report(assessment_key, level_key)
            filename = f"{assessment_key}_{level_key}.html"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Generated: {filename}")

if __name__ == "__main__":
    generate_all_reports()
