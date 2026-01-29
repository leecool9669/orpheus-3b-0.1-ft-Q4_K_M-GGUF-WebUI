from __future__ import annotations

import json
import random
import textwrap
import time
from typing import Tuple

import gradio as gr


MODEL_NAME = "Orpheus-3B-0.1-ft-Q4_K_M-GGUF"

VOICE_CHOICES = [
    "tara（通用女声）",
    "leah（温柔女声）",
    "jess（明亮女声）",
    "leo（青年男声）",
    "dan（沉稳男声）",
    "mia（活泼女声）",
    "zac（低沉男声）",
    "zoe（少年音）",
]

EMOTION_TAGS = [
    "中性 <neutral>",
    "愉悦 <laugh>",
    "悲伤 <cry>",
    "惊讶 <gasp>",
    "思考 <hmm>",
]


def _build_summary_text(
    text: str,
    voice: str,
    emotion: str,
    speed: float,
    temperature: float,
    top_p: float,
) -> str:
    """构造占位的 TTS 说明文本，用于在前端可视化展示生成配置与预期效果。"""
    preview = text.strip().replace("\n", " ")
    if len(preview) > 80:
        preview = preview[:80] + "…"

    return textwrap.dedent(
        f"""
        【占位合成结果说明】

        当前 WebUI 处于“轻量演示模式”，不会下载或加载任何真实的 Orpheus-3B 权重，也不会向外部服务发送请求。
        下述内容仅用于帮助用户从界面层面理解文本转语音系统的配置方式与感知效果：

        · 目标模型：{MODEL_NAME}
        · 选定音色：{voice}
        · 情感标签：{emotion}
        · 语速倍率：约为标准语速的 {speed:.2f} 倍
        · 采样控制：temperature={temperature:.2f}, top_p={top_p:.2f}

        · 文本摘要:" {preview} "

        在真实部署环境中，本区域将展示：
        1）生成语音的主观描述（音色、情感、语速等）；
        2）若干客观指标（流式延迟、生成时长、输出长度等）；
        3）与历史合成记录的对比结果，用于评估参数调节带来的差异。
        """
    ).strip()


def generate_tts_demo(
    text: str,
    voice: str,
    emotion: str,
    speed: float,
    temperature: float,
    top_p: float,
) -> Tuple[str, str]:
    """占位推理函数：模拟 Orpheus-3B 文本转语音推理过程，不进行真实合成。"""
    start = time.time()

    if not text or not text.strip():
        metrics = {
            "status": "empty-input",
            "note": "请先在左侧输入待合成的文本。",
            "mode": "demo",
        }
        return "请先在左侧输入一段需要合成的文本，再点击下方按钮触发占位推理。", json.dumps(
            metrics, ensure_ascii=False, indent=2
        )

    description = _build_summary_text(
        text=text,
        voice=voice,
        emotion=emotion,
        speed=speed,
        temperature=temperature,
        top_p=top_p,
    )

    latency_ms = int((time.time() - start) * 1000) + random.randint(50, 150)
    pseudo_duration = max(1.5, min(18.0, len(text) / 12.0))

    metrics = {
        "mode": "demo",
        "status": "ok",
        "latency_ms": latency_ms,
        "estimated_audio_duration_s": round(pseudo_duration, 2),
        "voice": voice,
        "emotion": emotion,
        "speed_ratio": round(speed, 2),
        "sampling": {
            "temperature": round(temperature, 2),
            "top_p": round(top_p, 2),
        },
        "note": "当前为占位输出，用于界面与参数调节可视化展示，不调用真实 TTS 模型。",
    }

    return description, json.dumps(metrics, ensure_ascii=False, indent=2)


with gr.Blocks(
    title=f"{MODEL_NAME} WebUI Demo",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown(
        textwrap.dedent(
            f"""
            # {MODEL_NAME} 文本转语音 WebUI 演示界面

            本界面以占位推理的方式，展示 Orpheus-3B 量化模型在本地部署场景下的
            典型交互流程，包括文本输入、音色与情感配置、采样参数调节以及合成结果的
            结构化可视化。当前实现不加载任何真实权重，也不会访问外部推理服务。
            """
        )
    )

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 文本输入与参数配置")
            text = gr.Textbox(
                label="待合成文本",
                lines=6,
                placeholder="例如：在本地环境中，我们使用 Orpheus-3B 模型合成具有情感与节奏控制的高质量语音。",
                value="在本地环境中，我们使用 Orpheus-3B 模型合成具有情感与节奏控制的高质量语音。",
            )

            voice = gr.Dropdown(
                label="音色选择（voice）",
                choices=VOICE_CHOICES,
                value=VOICE_CHOICES[0],
            )

            emotion = gr.Dropdown(
                label="情感标签（emotion tag）",
                choices=EMOTION_TAGS,
                value=EMOTION_TAGS[0],
            )

            with gr.Row():
                speed = gr.Slider(
                    minimum=0.7,
                    maximum=1.4,
                    step=0.05,
                    value=1.0,
                    label="语速倍率",
                )
                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=1.5,
                    step=0.05,
                    value=0.6,
                    label="temperature",
                )
                top_p = gr.Slider(
                    minimum=0.1,
                    maximum=1.0,
                    step=0.05,
                    value=0.9,
                    label="top_p",
                )

            run_btn = gr.Button("生成占位合成结果（不实际调用模型）", variant="primary")

        with gr.Column(scale=3):
            gr.Markdown("### 合成结果说明与指标可视化")
            description = gr.Textbox(
                label="合成结果描述（占位）",
                lines=14,
                interactive=False,
            )
            metrics_view = gr.Code(
                label="推理指标/配置摘要（JSON，占位）",
                language="json",
                lines=14,
            )

    run_btn.click(
        fn=generate_tts_demo,
        inputs=[text, voice, emotion, speed, temperature, top_p],
        outputs=[description, metrics_view],
    )


if __name__ == "__main__":
    # 使用固定端口以便自动化截图与验收
    demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
