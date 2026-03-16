import type { DailyReport } from "@/types/daily";

export const report: DailyReport = {
  date: "2026-03-14",
  title: "2026年3月14日 AI论文日报",
  summary:
    "本期围绕一个小批量但非空的计算机视觉窗口做闭环演练，共扫描到 4 篇候选论文。最值得深读的工作来自医学影像方向，它没有继续单纯追求更锐利的生成结果，而是把“哪些区域值得相信”纳入扩散采样过程，强调结构一致性与临床可靠性。其余论文则分别覆盖了自动驾驶多模态问答、具身辅助控制以及图像复原网络结构，反映出当前视觉研究正在同时推进系统可靠性、跨模态理解和基础架构稳健性。整体来看，本期论文的共同趋势是：模型能力不再只看平均性能，而越来越强调在复杂环境中的可信表现。",
  totalPapers: 4,
  tags: ["医学影像", "多模态理解", "自动驾驶", "图像复原"],
  trends:
    "这批论文共同体现出一个方向：视觉模型的竞争重点正在从“能不能做出来”转向“在噪声、失效和不确定条件下还能否稳定可信地工作”。",
  highlights: [
    {
      arxivId: "2603.11325v1",
      title:
        "Towards Trustworthy Selective Generation: Reliability-Guided Diffusion for Ultra-Low-Field to High-Field MRI Synthesis",
      authors: [
        "Zhenxuan Zhang",
        "Peiyuan Jing",
        "Ruicheng Yuan",
        "Liwei Hu",
        "Anbang Wang",
        "Fanwen Wang",
        "Yinzhe Wu",
        "Kh Tohidul Islam",
        "Zhaolin Chen",
        "Zi Wang",
        "Peter Lally",
        "Guang Yang",
      ],
      abstract:
        "Low-field to high-field MRI synthesis has emerged as a cost-effective strategy to enhance image quality under hardware and acquisition constraints, particularly in scenarios where access to high-field scanners is limited or impractical. Despite recent progress in diffusion models, diffusion-based approaches often struggle to balance fine-detail recovery and structural fidelity. In particular, the uncontrolled generation of high-resolution details in structurally ambiguous regions may introduce anatomically inconsistent patterns, such as spurious edges or artificial texture variations. These artifacts can bias downstream quantitative analysis. For example, they may cause inaccurate tissue boundary delineation or erroneous volumetric estimation, ultimately reducing clinical trust in synthesized images. These limitations highlight the need for generative models that are not only visually accurate but also spatially reliable and anatomically consistent. To address this issue, we propose a reliability-aware diffusion framework (ReDiff) that improves synthesis robustness at both the sampling and post-generation stages. Specifically, we introduce a reliability-guided sampling strategy to suppress unreliable responses during the denoising process. We further develop an uncertainty-aware multi-candidate selection scheme to enhance the reliability of the final prediction. Experiments on multi-center MRI datasets demonstrate improved structural fidelity and reduced artifacts compared with state-of-the-art methods.",
      categories: ["cs.CV"],
      arxivUrl: "https://arxiv.org/abs/2603.11325v1",
      tldr: "用可靠性感知扩散降低 MRI 合成幻觉细节。",
      problem:
        "论文关注超低场 MRI 向高场 MRI 合成时常见的结构失真问题。现有扩散模型虽然能补细节，但在证据不足的区域容易生成伪边界和假纹理，进而影响分割、体积估计等下游分析的可信度。",
      methodology:
        "作者提出 ReDiff，把“空间位置是否可靠”显式加入扩散生成流程。方法包含两层机制：其一是在采样阶段引入 reliability-guided sampling，通过可靠性图抑制不稳定区域的高频放大；其二是在生成后增加 uncertainty-aware candidate selection，对多次采样结果做一致性筛选与加权聚合，从而减少空间上不可信的重建结果。",
      keyFindings: [
        "在多中心 64mT 到 3T 的 MRI 合成实验中，ReDiff 在 PSNR、SSIM、LPIPS 等指标上整体优于或接近现有强基线。",
        "论文展示的方法不仅提升视觉清晰度，更重点减少了结构上不可信的高频伪影和人工纹理。",
        "可靠性引导采样与候选选择两步组合，比单纯依赖标准扩散去噪更能稳定控制空间不一致问题。",
      ],
      significance:
        "这项工作的重要性不只是做出更好看的 MRI，而是把“模型什么时候不该自信地补细节”变成了生成过程中的核心约束。对医疗场景而言，这种面向可靠性的设计比单纯追求平均像素质量更接近真实落地需求。",
      limitations:
        "基于可提取全文判断，论文当前验证仍集中在配对的低场到高场 MRI 合成任务上，结论对更广泛医学影像生成场景或临床部署收益的外推还需要更多证据。",
    },
  ],
  notables: [
    {
      arxivId: "2603.11380v1",
      title:
        "DriveXQA: Cross-modal Visual Question Answering for Adverse Driving Scene Understanding",
      authors: [
        "Mingzhe Tao",
        "Ruiping Liu",
        "Junwei Zheng",
        "Yufan Chen",
        "Kedi Ying",
        "M. Saquib Sarfraz",
        "Kailun Yang",
        "Jiaming Zhang",
        "Rainer Stiefelhagen",
      ],
      abstract:
        "Fusing sensors with complementary modalities is crucial for maintaining a stable and comprehensive understanding of abnormal driving scenes. However, Multimodal Large Language Models (MLLMs) are underexplored for leveraging multi-sensor information to understand adverse driving scenarios in autonomous vehicles. To address this gap, we propose the DriveXQA, a multimodal dataset for autonomous driving VQA. In addition to four visual modalities, five sensor failure cases, and five weather conditions, it includes $102,505$ QA pairs categorized into three types: global scene level, allocentric level, and ego-vehicle centric level. Since no existing MLLM framework adopts multiple complementary visual modalities as input, we design MVX-LLM, a token-efficient architecture with a Dual Cross-Attention (DCA) projector that fuses the modalities to alleviate information redundancy. Experiments demonstrate that our DCA achieves improved performance under challenging conditions such as foggy (GPTScore: $53.5$ vs. $25.1$ for the baseline). The established dataset and source code will be made publicly available.",
      categories: ["cs.CV"],
      arxivUrl: "https://arxiv.org/abs/2603.11380v1",
      tldr: "面向恶劣驾驶场景的多模态问答基准。",
      comment:
        "这篇工作把多天气、多传感器失效和驾驶问答任务放到一起评估，信息密度很高，适合作为自动驾驶多模态理解和鲁棒性评测的跟进对象。",
    },
    {
      arxivId: "2603.11346v1",
      title:
        "Learning to Assist: Physics-Grounded Human-Human Control via Multi-Agent Reinforcement Learning",
      authors: [
        "Yuto Shibata",
        "Kashu Yamazaki",
        "Lalit Jayanti",
        "Yoshimitsu Aoki",
        "Mariko Isogawa",
        "Katerina Fragkiadaki",
      ],
      abstract:
        "Humanoid robotics has strong potential to transform daily service and caregiving applications. Although recent advances in general motion tracking within physics engines (GMT) have enabled virtual characters and humanoid robots to reproduce a broad range of human motions, these behaviors are primarily limited to contact-less social interactions or isolated movements. Assistive scenarios, by contrast, require continuous awareness of a human partner and rapid adaptation to their evolving posture and dynamics. In this paper, we formulate the imitation of closely interacting, force-exchanging human-human motion sequences as a multi-agent reinforcement learning problem. We jointly train partner-aware policies for both the supporter (assistant) agent and the recipient agent in a physics simulator to track assistive motion references. To make this problem tractable, we introduce a partner policies initialization scheme that transfers priors from single-human motion-tracking controllers, greatly improving exploration. We further propose dynamic reference retargeting and contact-promoting reward, which adapt the assistant's reference motion to the recipient's real-time pose and encourage physically meaningful support. We show that AssistMimic is the first method capable of successfully tracking assistive interaction motions on established benchmarks, demonstrating the benefits of a multi-agent RL formulation for physically grounded and socially aware humanoid control.",
      categories: ["cs.CV", "cs.GR", "cs.RO"],
      arxivUrl: "https://arxiv.org/abs/2603.11346v1",
      tldr: "多智能体强化学习建模具身辅助协作。",
      comment:
        "它把带接触的人际辅助动作建模为多智能体控制问题，既有具身智能价值，也很适合观察未来机器人照护与服务场景的训练范式。",
    },
    {
      arxivId: "2603.11323v1",
      title: "UNet-AF: An alias-free UNet for image restoration",
      authors: [
        "Jérémy Scanvic",
        "Quentin Barthélemy",
        "Julián Tachella",
      ],
      abstract:
        "The simplicity and effectiveness of the UNet architecture makes it ubiquitous in image restoration, image segmentation, and diffusion models. They are often assumed to be equivariant to translations, yet they traditionally consist of layers that are known to be prone to aliasing, which hinders their equivariance in practice. To overcome this limitation, we propose a new alias-free UNet designed from a careful selection of state-of-the-art translation-equivariant layers. We evaluate the proposed equivariant architecture against non-equivariant baselines on image restoration tasks and observe competitive performance with a significant increase in measured equivariance. Through extensive ablation studies, we also demonstrate that each change is crucial for its empirical equivariance. Our implementation is available at https://github.com/jscanvic/UNet-AF",
      categories: ["cs.CV"],
      arxivUrl: "https://arxiv.org/abs/2603.11323v1",
      tldr: "无混叠 UNet 提升图像复原平移等变性。",
      comment:
        "这篇论文聚焦基础架构层面的稳健性改进，虽然问题很底层，但对图像复原和扩散模型中的 UNet 变体都有直接参考价值。",
    },
  ],
};
