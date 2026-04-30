#!/usr/bin/env python3.11
"""
批量生成全部12份心理测评PDF报告
- 韧性评估 A/B/C/D (4份)
- 焦虑类型 健康/容貌/关系/方向 (4份)
- 依附类型 安全/焦虑/回避/混乱 (4份)
"""
import os
from weasyprint import HTML

OUTPUT_DIR = "/workspace/psyche-assessment/reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 通用样式
# ============================================================
BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Noto Sans SC', sans-serif; color: #3A4F5C; background: white; padding: 40px 32px; max-width: 560px; margin: 0 auto; font-size: 14px; line-height: 1.7; }
.section-title { font-size: 16px; font-weight: 600; color: #3A4F5C; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #FAF3E8; }
.dim-card { margin-bottom: 16px; padding: 14px 16px; border-left: 3px solid #D4A574; background: #FAF3E8; border-radius: 0 8px 8px 0; }
.dim-card-title { font-size: 14px; font-weight: 600; color: #3A4F5C; margin-bottom: 4px; }
.dim-card-text { font-size: 13px; color: #4A6575; line-height: 1.7; }
.scene-card { display: flex; gap: 10px; margin-bottom: 10px; padding: 12px; background: #F7F7F7; border-radius: 8px; align-items: flex-start; }
.scene-emoji { font-size: 20px; flex-shrink: 0; }
.scene-text { font-size: 13px; color: #4A6575; line-height: 1.6; }
.action-card { display: flex; gap: 12px; margin-bottom: 12px; padding: 14px; background: #FAF3E8; border-radius: 12px; align-items: flex-start; }
.action-num { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #D4A574; color: white; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.action-text { font-size: 13px; color: #3A4F5C; line-height: 1.6; }
.knowledge-box { margin-bottom: 28px; padding: 18px; background: linear-gradient(135deg, #FAF3E8 0%, #F8DEDE 100%); border-radius: 12px; border: 1px dashed #E8C9A8; }
.knowledge-title { font-size: 14px; font-weight: 600; color: #C08B5A; margin-bottom: 8px; }
.knowledge-text { font-size: 13px; line-height: 1.7; color: #4A6575; }
.counselor-box { margin-bottom: 28px; padding: 28px 20px; background: linear-gradient(135deg, #D4A574 0%, #F2C4C4 100%); border-radius: 16px; text-align: center; color: white; }
.counselor-label { font-size: 12px; font-weight: 300; letter-spacing: 2px; opacity: 0.85; margin-bottom: 12px; }
.counselor-text { font-size: 16px; font-weight: 300; line-height: 1.8; font-style: italic; }
.cta-box { text-align: center; padding: 24px; border-top: 1px solid #EFEFEF; }
.cta-hint { font-size: 14px; color: #8C8C8C; margin-bottom: 12px; }
.cta-btn { display: inline-block; padding: 10px 32px; background: #D4A574; color: white; border-radius: 999px; font-size: 14px; font-weight: 500; }
.disclaimer { font-size: 11px; color: #B0B0B0; text-align: center; margin-bottom: 24px; }
.footer { font-size: 10px; color: #D9D9D9; text-align: center; margin-top: 20px; }
.positive-box { margin-bottom: 28px; padding: 18px; background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%); border-radius: 12px; border: 1px solid #C8E6C9; }
.positive-title { font-size: 14px; font-weight: 600; color: #2E7D32; margin-bottom: 8px; }
.partner-box { margin-bottom: 16px; padding: 14px 16px; border-left: 3px solid #27AE60; background: #E8F5E9; border-radius: 0 8px 8px 0; }
.partner-title { font-size: 14px; font-weight: 600; color: #2E7D32; margin-bottom: 4px; }
.trap-box { margin-bottom: 16px; padding: 14px 16px; border-left: 3px solid #E74C3C; background: #FFF3E0; border-radius: 0 8px 8px 0; }
.trap-title { font-size: 14px; font-weight: 600; color: #C62828; margin-bottom: 4px; }
"""

def cover_html(assessment_name, level_title, icon):
    return f"""
<div style="text-align: center; padding: 40px 0 32px; background: linear-gradient(135deg, #D4A574 0%, #F2C4C4 100%); border-radius: 16px; margin-bottom: 28px; color: white;">
    <div style="font-size: 40px; margin-bottom: 8px;">{icon}</div>
    <div style="font-size: 14px; letter-spacing: 3px; opacity: 0.85; margin-bottom: 12px;">心知·心理测评</div>
    <div style="font-size: 26px; font-weight: 700; margin-bottom: 8px;">{assessment_name}</div>
    <div style="font-size: 18px; font-weight: 300; opacity: 0.9;">{level_title}</div>
    <div style="font-size: 12px; margin-top: 16px; opacity: 0.7;">深度报告 · 个性化解读</div>
</div>
"""

# ============================================================
# 韧性评估报告 A/B/C/D
# ============================================================
RESILIENCE = {
    "name": "职场心理韧性评估",
    "icon": "🛡️",
    "levels": {
        "A": {
            "title": "等级A：心理韧性较弱",
            "evaluation": "先深呼吸一下。看到这个结果，你可能会有些失落，甚至觉得"果然如此"——但我想告诉你，你愿意花时间来做这个测评，本身就说明你还没有放弃自己，这份勇气值得被看见。你现在的状态，不是因为你不够好，而是你承受的压力已经远超一个人该扛的分量。",
            "dims": [
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
            "counselor": "你现在所处的状态，不叫"软弱"，叫"扛了太久"。一棵树在风暴中弯了腰，不是树的问题，是风太大了。请允许自己不那么坚强，允许自己需要帮助——这恰恰是最勇敢的选择。",
            "cta": "解锁完整深度报告，看见你的韧性力量"
        },
        "B": {
            "title": "等级B：心理韧性一般",
            "evaluation": "你好呀，你可能既不意外也不慌张——因为你心里其实清楚，自己有些地方做得还行，有些地方确实还在"硬撑"。好消息是，你已经具备了基础，只需要在关键点上精准发力。",
            "dims": [
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
            "counselor": "你不是不够好，你只是还在找那个最适合自己的节奏。就像跑马拉松，前半程不稳不代表跑不到终点——调整呼吸，找到自己的配速，你会越跑越稳的。",
            "cta": "解锁完整深度报告，找到你的精准发力点"
        },
        "C": {
            "title": "等级C：心理韧性良好",
            "evaluation": "你已经历练出了一套自己的"生存系统"，大部分时候都能稳住自己。不过，"良好"和"强韧"之间还有一段距离——那些偶尔冒出来的焦虑，说明你的系统还有可以优化的空间。",
            "dims": [
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
            "counselor": "你已经很棒了，不是客气话。接下来的路，不只是"扛住"，更是"活出来"——让韧性成为你选择生活的底气，而不只是应对压力的盔甲。",
            "cta": "解锁完整深度报告，让你的韧性从"良好"进阶到"强韧""
        },
        "D": {
            "title": "等级D：心理韧性强韧",
            "evaluation": "你已经走过了不少风雨，练就了一身在风浪中自如穿行的本领。不过，韧性高的人也有自己的"盲区"——你太能扛了，所以可能忽略了一些更深层的需求。",
            "dims": [
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
            "counselor": "你很强大，但强大不是不需要被照顾。你的韧性是天赋，也是你一砖一瓦建起来的城堡——但城堡里的人也需要阳光和花园。在帮助世界之前，先允许自己被这个世界温柔以待。",
            "cta": "解锁完整深度报告，看见你强大背后的深层需求"
        }
    }
}

# ============================================================
# 焦虑类型报告
# ============================================================
ANXIETY = {
    "name": "焦虑类型自测",
    "icon": "🌀",
    "types": {
        "health": {
            "title": "健康焦虑型——身体信号让我不安",
            "yourAnxietySays": "你的身体就像一个过分尽责的哨兵，每一个微小的信号它都会拉响警报。你的焦虑其实是在说："我太在乎这副身体了，我害怕失去健康后一切都会崩塌。"这种焦虑的根源，往往不是身体真的出了问题，而是你对"失控"的恐惧。",
            "dims": [
                ("健康焦虑（主要）", "你可能已经养成了"身体扫描"的习惯——每天不自觉地从头到脚检查一遍有没有异样。这种高度警觉让你很累，但也说明你是一个对身体负责的人。"),
                ("容貌焦虑", "你对身体信号的关注有时会延伸到外貌上——"我的脸是不是变差了"。身体和外貌在你这里常常连在一起。"),
                ("关系焦虑", "你的健康焦虑可能和关系焦虑有关——"如果我生病了，谁会照顾我？"对健康的担忧背后，藏着对"被照顾"的渴望。"),
                ("方向焦虑", "你有时会想，如果身体出了问题，现在努力的一切是不是都没有意义？")
            ],
            "scenes": [
                "凌晨两点的搜索：你因为胸口闷痛打开手机搜索，从"胸闷原因"一路点到"心梗前兆"，越看越害怕",
                "体检前的失眠：体检前一周你就开始紧张，前一天晚上反复想"万一查出来什么怎么办"",
                "身上"小毛病"的漫长关注：你发现身上有一颗痣好像比以前大了一点，心里一直悬着，但又不敢去医院"
            ],
            "positiveSide": "你的健康焦虑说明你是一个对身体高度负责的人。你的警觉是一种保护机制，只是现在它有点"用力过猛"了。焦虑不是你的敌人，它只是一个需要被调低音量的闹钟。",
            "actions": [
                "给搜索设限——想搜索身体症状时，先对自己说"我先等10分钟"，10分钟后只看权威医学科普网站",
                "写一次"身体感谢信"——写下3件你的身体今天为你做到的事",
                "做一次5分钟的身体扫描冥想——从头顶到脚尖缓慢"扫描"身体，不带评判地感受"
            ],
            "knowledge": "焦虑的"信号功能"：焦虑不是"坏东西"，它是一种信号功能——就像汽车仪表盘上的指示灯。灯亮了，不是让你把灯砸掉，而是提醒你看看哪里需要关注。",
            "counselor": "你的身体一直在努力保护你，而你的焦虑也在努力保护你——只是它们有时候太用力了。你不需要消灭这份担心，你只需要学会对它说："我听到了，谢谢你提醒我。"",
            "cta": "解锁完整行动方案，学会和你的健康焦虑和平共处"
        },
        "appearance": {
            "title": "容貌焦虑型——镜子里的我不够好",
            "yourAnxietySays": "你的焦虑在说："我只有足够好看，才值得被爱。"容貌焦虑的本质不是"你不够好看"，而是你把"被爱的资格"和"外貌"绑在了一起。你的焦虑其实在替你问一个更深的渴望："如果不完美，还会有人喜欢我吗？"",
            "dims": [
                ("容貌焦虑（主要）", "你可能很小就学会了"好看=被喜欢"这个等式，然后一直在为它买单。你的自我评价体系里，外貌占了太大的比重。"),
                ("健康焦虑", "你的容貌焦虑有时会伪装成健康焦虑——"皮肤变差了是不是身体出了问题？"你关注健康的起点，往往是外貌的变化。"),
                ("关系焦虑", "这是容貌焦虑最常见的"搭档"。你可能觉得"如果不够好看，ta就不会喜欢我了"，把外貌当作关系的入场券。"),
                ("方向焦虑", "你可能觉得"如果我更好看一点，人生会更顺利"——这种想法会加剧你对方向的不确定感。")
            ],
            "scenes": [
                "出门前的镜子拉锯战：换好衣服站在镜子前，总觉得哪里不对，换了三套还是不满意",
                "朋友圈的"修图地狱"：拍了一百张照片选不出一张能发的，修图修了半小时",
                "聚会中的"隐形比较"：忍不住比较——她皮肤比我好、比我瘦、穿搭比我好看"
            ],
            "positiveSide": "你的容貌焦虑说明你是一个对"美"有追求、有感知力的人。你不会"无所谓"，你在乎自己呈现给世界的样子——这本身就是一种生命力的体现。",
            "actions": [
                "拍一张"零修图"的照片，不修图不发朋友圈——只存给自己。写下三个你觉得"其实还不错"的地方",
                "社交媒体"断舍离"一天——不看别人的"精修人生"",
                "对镜子说一句温柔的话——具体的："你的眼睛笑起来很温暖""你今天有好好照顾自己""
            ],
            "knowledge": ""条件化自我价值"：当我们把自我价值建立在外部条件上（比如外貌），就会陷入"只有……才值得被爱"的循环。真正稳定的自我价值感来自内在——"我值得被爱，不是因为好看，而是因为我存在"。",
            "counselor": "你比你在镜子里看到的自己要丰富得多——你的笑容、你的善良、你认真生活的样子，这些都是"好看"无法概括的。容貌只是你的一扇窗，而不是你的全部。爱你的人，爱的从来不是那扇窗，而是窗里面那盏灯。",
            "cta": "解锁完整行动方案，重新定义你的"值得被爱""
        },
        "relationship": {
            "title": "关系焦虑型——我总怕被抛弃或误解",
            "yourAnxietySays": "你的焦虑在说："我害怕被丢下。"你可能学会了一件事——关系是不安全的，爱是需要争取的，而你可能随时会失去。你的焦虑不是"太作"或"太粘人"，它是一个曾经受过伤的小孩在说："请你别走。"",
            "dims": [
                ("关系焦虑（主要）", "你可能有一个"关系雷达"——时刻在扫描"ta是不是不高兴了"。这个雷达非常灵敏，但有时会把风吹草动误判为暴风预警。"),
                ("健康焦虑", "你的关系焦虑可能投射到身体上——"如果他不爱我了，我可能会生病"。身体成了你表达不安的另一种方式。"),
                ("容貌焦虑", "你可能在关系中最在意的就是"对方觉得我好看吗"——外貌在这里变成了关系的"保命符"。"),
                ("方向焦虑", "你可能会因为关系的不确定而影响对方向的判断——你的方向感有时是被关系状态绑定的。")
            ],
            "scenes": [
                "等消息的煎熬：5分钟没回就开始想"是不是我说的那句话不对"，30分钟后脑补了一整出大戏",
                "先道歉的那个人：明明不是自己的错，但你还是先发消息说"对不起"",
                "聚会中的"隐形人"焦虑：如果别人聊得火热你插不上话，你就会想"我是不是多余的那个""
            ],
            "positiveSide": "你的关系焦虑说明你是一个对情感有深度渴求和高度共情的人。你不是"太敏感"，你是在乎。你的焦虑是这份共情能力的"超载"——当你学会也把这份温柔给自己，你会成为一个既能爱人、也能被爱的人。",
            "actions": [
                "给"脑补"踩个刹车——写下三句话：我观察到的事实是什么？我脑补的故事是什么？另一种可能是什么？",
                "练习一次"不委屈自己"的表达——说出一句你真正想说的话",
                "给自己写一条"不离不弃"的承诺——"无论谁离开，我都不会离开自己。""
            ],
            "knowledge": "依恋理论：焦虑型依恋的人往往在关系中表现出"过度激活策略"——时刻保持警觉，试图抓住对方。但好消息是，依恋模式不是命运，通过觉察和练习，你可以发展出更安全的依恋方式。",
            "counselor": "你害怕被丢下，可你有没有发现——从始至终，那个一直没有离开你的人，是你自己？你比你想的要坚强，也比你想的更值得被好好对待。学会做自己的安全基地，你会发现，外面的关系没那么容易断。",
            "cta": "解锁完整行动方案，学会在爱中安心"
        },
        "direction": {
            "title": "方向焦虑型——我不知道该往哪走",
            "yourAnxietySays": "你的焦虑在说："我不甘心就这样，但我又不知道该怎样。"这是四种焦虑中最"哲学"的一种——它不是关于身体、外貌或某个人，它是关于"意义"。你之所以焦虑，恰恰是因为你在意。只有心里有一团火的人，才会觉得"这里不是我该待的地方"。",
            "dims": [
                ("方向焦虑（主要）", "你可能站在人生的十字路口，或者在一条路上走着但总觉得"不对"。你不是没有选择，而是选择太多、信息太杂。但请记住：没有"对的路"，只有"你走的路"。"),
                ("健康焦虑", "你的方向焦虑可能让你对身体格外敏感——"如果我身体垮了，还谈什么方向？""),
                ("容貌焦虑", "你有时会觉得"如果我更好看，机会是不是更多"。容貌焦虑在这里不是真的在意外貌，而是把"方向不明"的无力感转嫁到了"我能改变的外在"上。"),
                ("关系焦虑", "你可能在关系中也在寻找方向——"ta是不是对的人"。方向焦虑的人容易把关系当作"锚"。")
            ],
            "scenes": [
                "深夜的"人生三问"：凌晨一点躺在床上突然开始想——"我到底在干嘛？""这是我想要的生活吗？"",
                "朋友圈里的"同辈压力"：刷到同学晒offer、晒房本、晒结婚证，心里一沉——"大家都上岸了，就我还在海里扑腾"",
                ""什么都想做"的瘫痪状态：想学画画、想考研、想做自媒体……什么都想做，结果什么都没开始"
            ],
            "positiveSide": "你的方向焦虑说明你是一个不满足于"随便活活"的人。一个对人生没有期待的人不会焦虑方向——只有心里有"想要更好"的火种，才会觉得当下的路不够宽。你的焦虑是一种"生命动能"。",
            "actions": [
                "写一份"不想做的事"清单——与其想"我想做什么"，不如先写"我明确不想做的事"。排除法的力量比想象中大",
                "用"最小行动"测试一个方向——想学画画就画一笔，想做自媒体就发一条内容。方向不是想出来的，是试出来的",
                "和"过来人"聊15分钟——约一个你欣赏的人，只问一个问题："你是怎么找到现在这个方向的？""
            ],
            "knowledge": "接纳承诺疗法（ACT）：我们最大的痛苦不是"找不到答案"，而是"一直在等一个确定的答案才敢行动"。ACT鼓励我们带着不确定感往前走——就像开车穿越大雾，你不需要看清整条路，只需要看清前方10米就够了。",
            "counselor": "你不是没有方向，你只是在很多方向里选择了犹豫。犹豫不可怕，可怕的是因为犹豫而一直站着不动。走慢一点没关系，弯路也没关系——每一步都是路，包括你现在站着的这一步。大雾终会散的，而你要做的，只是迈出下一步。",
            "cta": "解锁完整行动方案，找到你的下一步"
        }
    }
}

# ============================================================
# 依附类型报告
# ============================================================
ATTACHMENT = {
    "name": "亲密关系依附类型测试",
    "icon": "💕",
    "types": {
        "secure": {
            "title": "安全型——你能安心地亲近和被爱",
            "yourStyle": "你在亲密关系中像一棵根系扎实的树——你可以安心地向对方伸展枝叶，也可以在风中保持自己的姿态。你既不会因为对方的靠近而窒息，也不会因为对方的暂时离开而崩塌。你慢慢建立了一种稳定的信念：我值得被好好爱，而爱我的人不会轻易离开。",
            "loveLanguage": "你表达爱的方式温暖而自然——你会主动关心对方，也愿意分享自己的感受。你渴望的爱，是一种"我看见你，你也看见我"的对等关系——不需要反复确认，就是那种"你在就好"的笃定感。",
            "relationshipPattern": [
                "TA临时说今晚要加班来不了约会，你虽然有点小失落，但还是说"没事你忙，我们改天"，然后给自己安排了一个舒服的晚上",
                "你们有分歧的时候，你能比较冷静地表达感受，也能倾听对方",
                "你会在TA难过时默默陪着，也会在自己脆弱时向TA求助"
            ],
            "bestPartner": "安全型是你最能有效"疗愈"的伴侣。焦虑型的人需要你的稳定回应和温暖在场。回避型也是你可以相处的类型，你的包容能让回避型的人感到安全。",
            "traps": ""我OK"的惯性：你太习惯自己消化情绪，有时候可能忽略了向对方表达需求|过度迁就：你的包容度高，可能让你在不合适的关系里待太久|忽视自己的不适：当对方的边界踩到你的底线时，你可能说服自己"没那么严重"",
            "actions": [
                "每周问自己一次："这周我有没有什么想表达但忍住没说的话？"如果有的话，用温和的方式告诉TA",
                "练习说"我也需要"——当TA问你怎么了，试着不说"没事"，而是说"我有点累，你能抱抱我吗？"",
                "给自己设一个"迁就底线"——在关系中列3件你绝对不会妥协的事"
            ],
            "knowledge": "安全型依附不是"天生"的，而是由"足够好的照料"累积形成的。如果你是安全型，感谢那些曾经稳稳接住你的人；如果你不是，安全型依附在任何年龄都可以通过好的关系经验被"挣得"（earned security）。",
            "counselor": "你能安心地爱，也能安心地被爱，这是很多人花了很久才学会的事。但请记得，你的"稳定"不是用来无限消耗的——允许自己偶尔不那么OK，也是一种对关系的信任。",
            "cta": "解锁双人报告，让你们的相处更懂彼此"
        },
        "anxious": {
            "title": "焦虑型——你总怕TA不够爱你",
            "yourStyle": "你在爱里像一只把心捧在手上的小鹿——每一步都小心翼翼，生怕走错了就再也回不来。你对关系中的每一个信号都超级敏感。你的不安不是"想太多"，而是你内心深处有一个声音一直在问："我是不是不够好，TA会不会不要我了？"",
            "loveLanguage": "你表达爱的方式是全心全意的投入和关注——你会记住TA喜欢的一切，会在TA不在的时候反复看聊天记录。你渴望的爱，是"你让我确信我是被选择的"——一句"我在"，对你来说比任何礼物都珍贵。",
            "relationshipPattern": [
                "TA说"今晚和同事聚餐"，你5分钟后就开始不安，10点还没动静你打开朋友圈发现TA点赞了别人但没回你消息",
                "吵架了，你很难做到"先冷静一下再聊"。沉默让你窒息——你一定要马上解决问题",
                "你为TA做了很多事，但当你感觉TA的回应不够热烈时，会有种"只有我在努力"的委屈"
            ],
            "bestPartner": "安全型是你最需要的伴侣。安全型的人稳定、温暖、不会因为你的情绪而逃跑，能给你最需要的东西——"我不会走"的确定感。注意：焦虑型+回避型是最容易陷入"追逐-逃跑"恶性循环的组合。",
            "traps": ""追确认"的无限循环：你需要的确认永远"不够"——不是因为对方给得少，而是你内心那个"我不够好"的声音太响了|把牺牲当爱：你容易把"为对方改变自己"当作爱的证明，但长此以往会失去自己|选择性关注负面信号：你容易忽略对方99次温暖的回应，只记住那1次的冷淡",
            "actions": [
                ""停三秒"练习：当你想发第五条消息确认TA在不在乎你的时候，停下来深呼吸三次。问自己："我现在的不安，是事实告诉我的，还是恐惧告诉我的？"",
                "建立"自我确认清单"：写下3件你为自己感到骄傲的事，贴在镜子上",
                "和TA约定"安心暗号"：告诉TA当你焦虑的时候你需要什么，而不是用发脾气来索取关注"
            ],
            "knowledge": "焦虑型依附的形成往往与"不一致的回应"有关——小时候，照料者有时热情回应、有时又缺席，让孩子始终处于不确定中。你的"用力"不是你的错，而是你小时候找到的生存智慧。只是长大后的你，值得一种更轻松的爱。",
            "counselor": "你那么用力地爱，是因为你太珍惜这段关系。但请记住：爱你的人，不需要你拼命证明自己值得。你的不安是在保护曾经的你，但现在的你，可以慢慢学着相信——有些人不会走，有些人光是你在那里就够了。你值得那种不用踮脚也能被看见的爱。",
            "cta": "解锁双人报告，走出"追确认"的循环"
        },
        "avoidant": {
            "title": "回避型——你习惯一个人，太近会不舒服",
            "yourStyle": "你在关系里像一只习惯了独行的猫——你能优雅地享受自己的生活，但当有人想太近地靠近，你会本能地后退一步。不是你不想被爱，而是"太近"这件事本身让你不舒服。你可能很擅长经营"搭子式"的关系——吃饭搭子、旅行搭子、聊天搭子，一切刚刚好。但当关系要从"搭子"升级为"我们"，你心里就会响起一个声音："还是算了吧，一个人挺好的。"",
            "loveLanguage": "你表达爱的方式往往不动声色——你可能不会说很多甜言蜜语，但你会默默帮TA解决一个麻烦、在TA生病时跑很远送药、记得TA无意提过的一个小愿望。你渴望的爱，是一种"不被吞噬的自由"——你希望有个人，既能让你安心靠近，又不会让你感到被围困。",
            "relationshipPattern": [
                "你们的关系越来越近，TA开始聊"以后"，你嘴上应着心里却在想"走一步看一步吧"，甚至开始下意识地找TA的缺点",
                "TA对你说"我好想你"，你回了一个"嗯嗯"然后迅速转移话题",
                "你的恋爱总是"开场还不错，后来就淡了"，每段关系走到某个深度你就觉得"好像也不是非要在一起""
            ],
            "bestPartner": "安全型是你最能放松下来的伴侣。安全型的人既温暖又不黏人，TA的靠近不会让你感到窒息。注意：回避型+焦虑型是最需要警惕的组合。焦虑型会不断向你索取确认和亲密，而这正是最让你想逃跑的东西。",
            "traps": ""还不错的单身"幻觉：你总觉得自己一个人也活得很好，但深夜里那种说不出口的空虚只有你自己知道|用"不合适"逃避亲密：每段关系到了要深入的节点，你就开始挑毛病、找退路|"不说就等于不受伤"：那些没说出口的感受会变成一堵墙，把真心想靠近你的人挡在外面",
            "actions": [
                "每天分享一件小事——不一定要深情告白，就从"今天看到一个很好笑的视频"开始，让对方走进你日常的世界",
                "写一条你从没说过的话——把你一直想说但没说出口的感受写在纸条上，哪怕只是让自己承认这件事",
                "设定"不逃跑时间"——当你想从一场深入的对话中撤退时，给自己一个规则：至少再待5分钟"
            ],
            "knowledge": "回避型依附的形成往往与"情感忽视"有关——小时候当你表达需求时，照料者没有回应，或者回应的方式让你觉得"我的感受不重要"。于是你学会了："既然得不到，那就不需要。"但人的大脑有一个矛盾的设计——你越压抑对亲密的渴望，它在潜意识里就越强烈。你的"不需要"不是真的不需要，而是一种聪明的自我保护。",
            "counselor": "你的独立让人敬佩，但独立和孤独之间只差一个字的距离。你不需要一次性把心门全打开——只需要留一条缝，让那个值得的人透一点光进来。你值得被爱，也值得在爱里做你自己——不是"一个人的自己"，而是"也可以安心依赖别人的自己"。",
            "cta": "解锁双人报告，学会在爱里安心靠近"
        },
        "fearful": {
            "title": "混乱型——你既渴望亲密又害怕受伤",
            "yourStyle": "你在关系里像站在海浪中——浪来了你往后躲，浪退了你又追上去。你渴望亲密，但当亲密真的到来时，你又害怕到想逃。你的内心好像同时住着两个人：一个说"快靠近TA，别让TA走"，另一个说"别靠太近，你一定会受伤"。你不是故意反复，你只是太想被爱，又太怕被爱伤害。",
            "loveLanguage": "你表达爱的方式是剧烈而矛盾的——你可能一会儿极其热情，为对方倾尽所有；一会儿又突然退缩，把对方推得远远的。你渴望的爱，是一种"即使我推开你，你也不会走"的绝对安全——你需要对方能在你的反复中依然坚定地站在那里。",
            "relationshipPattern": [
                "你们刚在一起时你全心投入，但关系一旦稳定下来你开始莫名焦虑——"是不是太好了？会不会出问题？"于是你开始制造冲突",
                "TA对你很好很体贴，但你总觉得不真实。你一边享受被照顾的温暖，一边在等"另一只鞋掉下来"",
                "你对亲密的人发完脾气，会立刻陷入巨大的自责和恐惧："TA会不会因此不要我了？""
            ],
            "bestPartner": "安全型是你最需要的"锚"。安全型的人能给你两样东西：温暖的靠近和稳定的在场。当你的焦虑发作时TA不会逃跑，当你的回避上线时TA不会逼迫。但请记住——安全型的人也有边界，你不能无限试探TA的耐心。",
            "traps": ""试探式亲密"：你用推开对方来测试"TA会不会留下来"，但每一次试探都在消耗对方的信任和耐心|自我实现的预言：你太害怕被抛弃，反而用反复无常把对方推走——然后告诉自己"看吧，果然没人会一直留在我身边"|情绪过山车：你的关系总是大起大落，以至于平静反而让你不安",
            "actions": [
                "学会命名你的感受——当你想发脾气或逃跑时，先对自己说："我现在不是真的生气/想走，我是害怕了。"给感受一个准确的名字，它就没那么容易控制你",
                "记录你的"关系心跳"——每天花1分钟写下你今天对关系的感受（1-10分），连续两周。你会发现：你以为是"对方变了"，其实是你的情绪在过山车",
                ""等24小时"规则——当你在情绪最高点想做一个重大决定时，强迫自己等24小时"
            ],
            "knowledge": "混乱型依附往往与"创伤性依恋经历"有关——小时候的照料者可能既是安全的来源，也是恐惧的来源。孩子于是陷入两难："我需要靠近这个人才能生存，但靠近这个人又会受伤。"这种"既想靠近又必须逃离"的矛盾，变成了你在成年关系中的底色。了解这一点不是为了怪谁，而是为了理解：你的矛盾是有来由的，而你也有能力写出新的剧本。",
            "counselor": "你的内心像一片海，有时候风平浪静，有时候巨浪滔天。你也许觉得自己太难搞、太反复、太难被爱——但我想告诉你：你的矛盾，恰恰说明你对爱有着最深的渴望和最真的勇气。你一次次受伤，又一次次打开心门，这本身就是了不起的勇敢。请给自己多一点耐心——学会在爱里安定下来，是你此生最值得的功课。",
            "cta": "解锁双人报告，在爱中找到你的锚"
        }
    }
}

# ============================================================
# HTML 生成函数
# ============================================================

def make_dim_cards(dims, colors=None):
    if colors is None:
        colors = ["#D4A574", "#F2C4C4", "#7EC8A0", "#3A4F5C"]
    items = []
    for i, (title, text) in enumerate(dims):
        c = colors[i % len(colors)]
        items.append(f'<div class="dim-card" style="border-left-color: {c};"><div class="dim-card-title">{title}</div><div class="dim-card-text">{text}</div></div>')
    return "\n".join(items)

def make_scene_cards(scenes):
    emojis = ["🏠", "💭", "🌙"]
    items = []
    for i, s in enumerate(scenes):
        e = emojis[i % len(emojis)]
        items.append(f'<div class="scene-card"><span class="scene-emoji">{e}</span><span class="scene-text">{s}</span></div>')
    return "\n".join(items)

def make_action_cards(actions):
    items = []
    for i, a in enumerate(actions):
        items.append(f'<div class="action-card"><span class="action-num">{i+1}</span><span class="action-text">{a}</span></div>')
    return "\n".join(items)

def generate_resilience_pdf(level_key):
    r = RESILIENCE["levels"][level_key]
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><style>{BASE_STYLE}</style></head><body>
{cover_html(RESILIENCE["name"], r["title"], RESILIENCE["icon"])}
<div class="disclaimer">本测评仅供参考，不构成专业心理诊断</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">📋 总体评价</div>
    <div style="font-size: 14px; line-height: 1.8; color: #4A6575;">{r["evaluation"]}</div>
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">🔍 维度深度解读</div>
    {make_dim_cards(r["dims"])}
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">💭 你可能的生活场景</div>
    {make_scene_cards(r["scenes"])}
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">🎯 本周3件改善行动</div>
    {make_action_cards(r["actions"])}
</div>

<div class="knowledge-box">
    <div class="knowledge-title">📚 心理学小知识</div>
    <div class="knowledge-text">{r["knowledge"]}</div>
</div>

<div class="counselor-box">
    <div class="counselor-label">咨询师寄语</div>
    <div class="counselor-text">{r["counselor"]}</div>
</div>

<div class="cta-box">
    <div class="cta-hint">如需更深入的个人成长方案</div>
    <div class="cta-btn">预约1对1咨询</div>
</div>
<div class="footer">心知·心理测评 | 仅供参考，不构成专业心理诊断</div>
</body></html>"""
    
    filepath = os.path.join(OUTPUT_DIR, f"resilience_{level_key}.pdf")
    HTML(string=html).write_pdf(filepath)
    print(f"  Generated: resilience_{level_key}.pdf")
    return filepath

def generate_anxiety_pdf(type_key):
    t = ANXIETY["types"][type_key]
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><style>{BASE_STYLE}</style></head><body>
{cover_html(ANXIETY["name"], t["title"], ANXIETY["icon"])}
<div class="disclaimer">本测评仅供参考，不构成专业心理诊断</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">💬 你的焦虑在说什么</div>
    <div style="font-size: 14px; line-height: 1.8; color: #4A6575;">{t["yourAnxietySays"]}</div>
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">🔍 四维度深度解读</div>
    {make_dim_cards(t["dims"])}
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">💭 你可能的生活场景</div>
    {make_scene_cards(t["scenes"])}
</div>

<div class="positive-box">
    <div class="positive-title">✨ 你的焦虑的另一面</div>
    <div style="font-size: 13px; line-height: 1.7; color: #2E7D32;">{t["positiveSide"]}</div>
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">🎯 本周3件改善行动</div>
    {make_action_cards(t["actions"])}
</div>

<div class="knowledge-box">
    <div class="knowledge-title">📚 心理学小知识</div>
    <div class="knowledge-text">{t["knowledge"]}</div>
</div>

<div class="counselor-box">
    <div class="counselor-label">咨询师寄语</div>
    <div class="counselor-text">{t["counselor"]}</div>
</div>

<div class="cta-box">
    <div class="cta-hint">如需更深入的行动方案</div>
    <div class="cta-btn">{t["cta"]}</div>
</div>
<div class="footer">心知·心理测评 | 仅供参考，不构成专业心理诊断</div>
</body></html>"""
    
    filepath = os.path.join(OUTPUT_DIR, f"anxiety_{type_key}.pdf")
    HTML(string=html).write_pdf(filepath)
    print(f"  Generated: anxiety_{type_key}.pdf")
    return filepath

def generate_attachment_pdf(type_key):
    t = ATTACHMENT["types"][type_key]
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><style>{BASE_STYLE}</style></head><body>
{cover_html(ATTACHMENT["name"], t["title"], ATTACHMENT["icon"])}
<div class="disclaimer">本测评仅供参考，不构成专业心理诊断</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">💕 你的依附风格</div>
    <div style="font-size: 14px; line-height: 1.8; color: #4A6575;">{t["yourStyle"]}</div>
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">💌 你的爱的语言</div>
    <div style="font-size: 14px; line-height: 1.8; color: #4A6575;">{t["loveLanguage"]}</div>
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">💭 你的关系模式</div>
    {make_scene_cards(t["relationshipPattern"])}
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">💑 最佳伴侣类型</div>
    <div class="partner-box">
        <div class="partner-title">谁最适合你？</div>
        <div style="font-size: 13px; line-height: 1.7; color: #2E7D32;">{t["bestPartner"]}</div>
    </div>
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">⚠️ 你的关系陷阱</div>
    <div class="trap-box">
        <div class="trap-title">需要警惕的模式</div>
        <div style="font-size: 13px; line-height: 1.7; color: #C62828;">{t["traps"]}</div>
    </div>
</div>

<div style="margin-bottom: 28px;">
    <div class="section-title">🎯 本周3件改善行动</div>
    {make_action_cards(t["actions"])}
</div>

<div class="knowledge-box">
    <div class="knowledge-title">📚 心理学小知识</div>
    <div class="knowledge-text">{t["knowledge"]}</div>
</div>

<div class="counselor-box">
    <div class="counselor-label">咨询师寄语</div>
    <div class="counselor-text">{t["counselor"]}</div>
</div>

<div class="cta-box">
    <div class="cta-hint">如需更深入的关系改善方案</div>
    <div class="cta-btn">{t["cta"]}</div>
</div>
<div class="footer">心知·心理测评 | 仅供参考，不构成专业心理诊断</div>
</body></html>"""
    
    filepath = os.path.join(OUTPUT_DIR, f"attachment_{type_key}.pdf")
    HTML(string=html).write_pdf(filepath)
    print(f"  Generated: attachment_{type_key}.pdf")
    return filepath

# ============================================================
# 主函数：生成全部12份报告
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("批量生成心理测评PDF报告")
    print("=" * 50)
    
    print("\n[1/3] 韧性评估报告 (A/B/C/D)...")
    for key in ["A", "B", "C", "D"]:
        generate_resilience_pdf(key)
    
    print("\n[2/3] 焦虑类型报告 (健康/容貌/关系/方向)...")
    for key in ["health", "appearance", "relationship", "direction"]:
        generate_anxiety_pdf(key)
    
    print("\n[3/3] 依附类型报告 (安全/焦虑/回避/混乱)...")
    for key in ["secure", "anxious", "avoidant", "fearful"]:
        generate_attachment_pdf(key)
    
    print("\n" + "=" * 50)
    print(f"全部12份PDF报告已生成到: {OUTPUT_DIR}")
    print("=" * 50)
