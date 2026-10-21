import streamlit as st

__all__ = ["apply_global_styles", "render_footer", "style_plotly_chart"]


def apply_global_styles() -> None:
	"""Apply the shared visual theme to the active Streamlit page."""
	st.markdown(
		"""
		<style>
		:root {
			--finance-ink: #202344;
			--finance-muted: #727791;
			--finance-indigo: #4f46c8;
			--finance-violet: #7963df;
			--finance-teal: #168c83;
			--finance-border: rgba(83, 91, 145, 0.13);
		}

		[data-testid="stAppViewContainer"] {
			background: linear-gradient(135deg, #f7f8ff 0%, #f5f8fc 48%, #f1f8f7 100%);
		}

		[data-testid="stHeader"] {
			background: rgba(247, 248, 255, 0.76);
		}

		.main .block-container {
			max-width: 1500px;
			padding-top: 2rem;
			padding-bottom: 3rem;
		}

		[data-testid="stSidebar"] {
			background: linear-gradient(180deg, #202344 0%, #29264f 58%, #263d50 100%);
		}

		[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
		[data-testid="stSidebar"] [data-testid="stPageLink"] a {
			color: #eef0ff;
		}

		[data-testid="stSidebar"] [data-testid="stPageLink"] a {
			border-color: transparent;
			background: transparent;
		}

		[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
			border-color: rgba(238, 240, 255, 0.2);
			background: rgba(255, 255, 255, 0.1);
			color: #ffffff;
		}

		h1, h2, h3 {
			color: var(--finance-ink);
			font-family: "Aptos", "Segoe UI", sans-serif;
			letter-spacing: 0;
		}

		.main h1 {
			font-weight: 760;
			margin-bottom: 0.25rem;
		}

		.main [data-testid="stCaptionContainer"] {
			color: var(--finance-muted);
			font-size: 1rem;
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
			position: relative;
			min-height: 132px;
			padding: 1.15rem 1.25rem 1rem;
			border: 1px solid var(--finance-border);
			border-radius: 18px;
			background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(246, 246, 255, 0.96));
			box-shadow: 0 10px 30px rgba(43, 47, 91, 0.08), 0 2px 7px rgba(43, 47, 91, 0.035);
			transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"]:hover {
			transform: translateY(-2px);
			border-color: rgba(93, 83, 204, 0.28);
			box-shadow: 0 15px 34px rgba(43, 47, 91, 0.12), 0 3px 9px rgba(43, 47, 91, 0.05);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
			border-top: 3px solid #5c52d6;
			background: linear-gradient(145deg, #ffffff 8%, #f1f0ff 100%);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
			border-top: 3px solid #d36e78;
			background: linear-gradient(145deg, #ffffff 8%, #fff3f4 100%);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
			border-top: 3px solid #168c83;
			background: linear-gradient(145deg, #ffffff 8%, #edf9f7 100%);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
			border-top: 3px solid #9872d8;
			background: linear-gradient(145deg, #ffffff 8%, #f7f1ff 100%);
		}

		.st-key-finance-dashboard-kpis [data-testid="stMetric"]::after {
			position: absolute;
			top: 0.9rem;
			right: 1rem;
			padding: 0.22rem 0.58rem;
			border: 1px solid rgba(97, 86, 196, 0.14);
			border-radius: 999px;
			background: rgba(239, 237, 255, 0.84);
			color: #554bb4;
			content: "30 өдөр";
			font-size: 0.68rem;
			font-weight: 700;
			line-height: 1.35;
		}

		.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]::after {
			border-color: rgba(201, 92, 107, 0.18);
			background: #fff0f1;
			color: #a94f5c;
			content: "30 өдөр";
		}

		.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]::after {
			border-color: rgba(22, 140, 131, 0.2);
			background: #e8f7f4;
			color: #11756e;
			content: "Орлого − зарлага";
		}

		.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]::after {
			border-color: rgba(129, 95, 199, 0.2);
			background: #f2edff;
			color: #7050b2;
			content: "Хяналт";
		}

		.st-key-finance-dashboard-kpis [data-testid="stMetricLabel"] {
			padding-right: 5.5rem;
		}

		[data-testid="stMetricLabel"] {
			color: #626985;
			font-size: 0.86rem;
			font-weight: 650;
		}

		[data-testid="stMetricValue"] {
			margin-top: 0.55rem;
			color: var(--finance-ink);
			font-size: 1.7rem;
			font-weight: 760;
			line-height: 1.2;
		}

		[data-testid="stPageLink"] a,
		.stButton > button {
			border: 1px solid rgba(87, 79, 183, 0.2);
			border-radius: 12px;
			background: linear-gradient(135deg, #ffffff, #f5f3ff);
			color: #403a9a;
			font-weight: 650;
			transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
		}

		[data-testid="stPageLink"] a:hover,
		.stButton > button:hover {
			transform: translateY(-1px);
			border-color: rgba(87, 79, 183, 0.45);
			box-shadow: 0 7px 18px rgba(57, 55, 123, 0.1);
			color: #302878;
		}

		[data-testid="stPlotlyChart"] {
			padding: 0.5rem;
			border: 1px solid var(--finance-border);
			border-radius: 18px;
			background: rgba(255, 255, 255, 0.82);
			box-shadow: 0 8px 25px rgba(43, 47, 91, 0.055);
		}

		.finance-footer {
			margin-top: 3rem;
			padding: 1.1rem 0 0.35rem;
			border-top: 1px solid var(--finance-border);
			color: var(--finance-muted);
			font-size: 0.82rem;
			text-align: center;
		}

		@media (max-width: 760px) {
			.main .block-container {
				padding: 1.25rem 1rem 2rem;
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
				min-height: 118px;
				padding: 1rem;
				border-radius: 15px;
			}

			.st-key-finance-dashboard-kpis [data-testid="stMetric"]::after {
				top: 0.7rem;
				right: 0.7rem;
			}

			[data-testid="stMetricValue"] {
				font-size: 1.35rem;
			}
		}

		:root {
			color-scheme: dark;
			--finance-ink: #f4f2ff;
			--finance-muted: #aaa9c3;
			--finance-indigo: #8980ff;
			--finance-violet: #bd8cff;
			--finance-teal: #42e6d0;
			--finance-emerald: #66e7a8;
			--finance-border: rgba(204, 203, 255, 0.14);
		}

		[data-testid="stAppViewContainer"] {
			background-color: #0b0c13;
			background-image: linear-gradient(135deg, #0b0c13 0%, #121322 48%, #0e1719 100%);
			color: var(--finance-ink);
		}

		[data-testid="stHeader"] {
			background: rgba(11, 12, 19, 0.78);
		}

		.main .block-container {
			color: var(--finance-ink);
		}

		[data-testid="stSidebar"] {
			border-right: 1px solid rgba(187, 177, 255, 0.15);
			background: linear-gradient(165deg, #10111d 0%, #19172b 58%, #102320 100%);
			box-shadow: 12px 0 40px rgba(0, 0, 0, 0.22);
		}

		[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
		[data-testid="stSidebar"] [data-testid="stPageLink"] a {
			color: #e9e7ff;
		}

		.main h1, .main h2, .main h3 {
			color: #f3f0ff;
		}

		.main [data-testid="stCaptionContainer"] {
			color: #aaa9c3;
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
			border: 1px solid rgba(219, 216, 255, 0.16);
			border-radius: 16px;
			background: linear-gradient(145deg, rgba(34, 35, 54, 0.78), rgba(20, 23, 35, 0.7));
			box-shadow: 0 18px 42px rgba(0, 0, 0, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.07);
			backdrop-filter: blur(12px);
			-webkit-backdrop-filter: blur(12px);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
			border-top: 2px solid #8b80ff;
			background: linear-gradient(145deg, rgba(44, 40, 78, 0.76), rgba(20, 22, 35, 0.72));
			box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(184, 174, 255, 0.17), inset 0 0 24px rgba(118, 101, 255, 0.06);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
			border-top: 2px solid #ff789b;
			background: linear-gradient(145deg, rgba(65, 36, 58, 0.7), rgba(24, 21, 33, 0.74));
			box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 177, 198, 0.14), inset 0 0 24px rgba(255, 92, 139, 0.05);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
			border-top: 2px solid #42e6d0;
			background: linear-gradient(145deg, rgba(25, 61, 61, 0.72), rgba(17, 27, 35, 0.75));
			box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(146, 255, 231, 0.14), inset 0 0 24px rgba(43, 224, 203, 0.05);
		}

		[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
			border-top: 2px solid #bd8cff;
			background: linear-gradient(145deg, rgba(53, 40, 69, 0.74), rgba(23, 22, 37, 0.74));
			box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(222, 189, 255, 0.15), inset 0 0 24px rgba(178, 111, 255, 0.05);
		}

		[data-testid="stMetricLabel"] {
			color: #b8b6cf;
		}

		[data-testid="stMetricValue"] {
			color: #f6f4ff;
			text-shadow: 0 0 20px rgba(157, 139, 255, 0.13);
		}

		.st-key-finance-dashboard-kpis [data-testid="stMetric"]::after {
			border-color: rgba(176, 165, 255, 0.28);
			background: rgba(126, 107, 255, 0.17);
			color: #c9c1ff;
		}

		.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]::after {
			border-color: rgba(255, 120, 155, 0.28);
			background: rgba(255, 104, 142, 0.13);
			color: #ffafc3;
		}

		.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]::after {
			border-color: rgba(66, 230, 208, 0.3);
			background: rgba(42, 205, 184, 0.13);
			color: #84f2df;
		}

		.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]::after {
			border-color: rgba(189, 140, 255, 0.3);
			background: rgba(171, 113, 255, 0.14);
			color: #dab8ff;
		}

		[data-testid="stPlotlyChart"],
		[data-testid="stDataFrame"],
		[data-testid="stDataEditor"],
		[data-testid="stTable"],
		[data-testid="stForm"],
		[data-testid="stVerticalBlockBorderWrapper"] {
			border: 1px solid rgba(204, 203, 255, 0.13);
			border-radius: 16px;
			background: linear-gradient(145deg, rgba(27, 29, 46, 0.72), rgba(16, 19, 31, 0.64));
			box-shadow: 0 16px 38px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.045);
			backdrop-filter: blur(10px);
			-webkit-backdrop-filter: blur(10px);
		}

		[data-testid="stVerticalBlockBorderWrapper"] {
			padding: 0.85rem;
		}

		[data-testid="stPlotlyChart"] {
			padding: 0.5rem;
			background: rgba(18, 20, 32, 0.68);
		}

		[data-testid="stDataFrame"],
		[data-testid="stDataEditor"],
		[data-testid="stTable"] {
			overflow: hidden;
		}

		[data-testid="stTextInput"] input,
		[data-testid="stNumberInput"] input,
		[data-testid="stDateInput"] input,
		[data-testid="stTextArea"] textarea,
		[data-testid="stTimeInput"] input,
		[data-baseweb="select"] > div,
		[data-testid="stFileUploaderDropzone"] {
			border: 1px solid rgba(196, 193, 255, 0.18);
			border-radius: 12px;
			background: rgba(18, 20, 33, 0.78);
			color: #f2f0ff;
			box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
			backdrop-filter: blur(8px);
			-webkit-backdrop-filter: blur(8px);
		}

		[data-testid="stTextInput"] input:focus,
		[data-testid="stNumberInput"] input:focus,
		[data-testid="stDateInput"] input:focus,
		[data-testid="stTextArea"] textarea:focus,
		[data-testid="stTimeInput"] input:focus,
		[data-baseweb="select"] > div:focus-within {
			border-color: #8980ff;
			box-shadow: 0 0 0 1px rgba(137, 128, 255, 0.38), 0 0 18px rgba(137, 128, 255, 0.12);
		}

		[data-baseweb="popover"] [role="listbox"],
		[data-baseweb="menu"],
		[data-baseweb="popover"] [role="option"] {
			border: 1px solid rgba(204, 203, 255, 0.16);
			border-radius: 12px;
			background: #191a29;
			color: #f2f0ff;
			box-shadow: 0 18px 44px rgba(0, 0, 0, 0.38);
		}

		[data-baseweb="popover"] [role="option"]:hover,
		[data-baseweb="popover"] [aria-selected="true"] {
			background: linear-gradient(100deg, rgba(112, 94, 226, 0.35), rgba(37, 171, 155, 0.2));
			color: #ffffff;
		}

		[data-baseweb="tag"] {
			border: 1px solid rgba(66, 230, 208, 0.25);
			border-radius: 999px;
			background: rgba(39, 185, 163, 0.14);
			color: #a5fff0;
		}

		[data-testid="stTabs"] [data-baseweb="tab-list"] {
			gap: 0.35rem;
			border-bottom: 1px solid rgba(204, 203, 255, 0.13);
		}

		[data-testid="stTabs"] [data-baseweb="tab"] {
			border-radius: 10px 10px 0 0;
			color: #aaa9c3;
		}

		[data-testid="stTabs"] [aria-selected="true"] {
			background: linear-gradient(180deg, rgba(132, 117, 255, 0.16), rgba(132, 117, 255, 0.035));
			color: #e4deff;
		}

		[data-testid="stCheckbox"] label,
		[data-testid="stRadio"] label,
		[data-testid="stToggle"] label {
			color: #d1cfe4;
		}

		input[type="checkbox"],
		input[type="radio"] {
			accent-color: #8b80ff;
		}

		[data-testid="stExpander"] {
			border: 1px solid rgba(204, 203, 255, 0.14);
			border-radius: 14px;
			background: rgba(23, 25, 39, 0.55);
			backdrop-filter: blur(10px);
			-webkit-backdrop-filter: blur(10px);
		}

		[data-testid="stProgress"] > div > div > div {
			background: linear-gradient(90deg, #7665f5, #b876ff 56%, #35dfc5);
			box-shadow: 0 0 16px rgba(112, 94, 226, 0.32);
		}

		[data-testid="stAlert"] p,
		[data-testid="stToast"] p {
			color: #eceaff;
		}

		[data-testid="stFileUploaderDropzone"] {
			border-style: dashed;
			border-color: rgba(137, 128, 255, 0.42);
		}

		[data-testid="stFileUploaderDropzone"]:hover {
			border-color: #42e6d0;
			background: rgba(35, 51, 59, 0.82);
			box-shadow: 0 0 22px rgba(66, 230, 208, 0.09);
		}

		[data-testid="stDataFrame"] *,
		[data-testid="stDataEditor"] * {
			--gdg-bg-cell: rgba(22, 24, 38, 0.94);
			--gdg-bg-cell-medium: rgba(29, 31, 49, 0.96);
			--gdg-bg-header: rgba(34, 34, 55, 0.98);
			--gdg-text-dark: #eeecff;
			--gdg-text-medium: #b7b5cf;
			--gdg-border-color: rgba(204, 203, 255, 0.12);
		}

		label, [data-testid="stWidgetLabel"] p {
			color: #d1cfe4;
		}

		[data-testid="stPageLink"] a,
		.stButton > button,
		[data-testid="stFormSubmitButton"] button,
		[data-testid="stDownloadButton"] button {
			border: 1px solid rgba(174, 163, 255, 0.3);
			border-radius: 12px;
			background: linear-gradient(115deg, #6557e8 0%, #9862e8 55%, #20a995 125%);
			color: #ffffff;
			font-weight: 700;
			box-shadow: 0 8px 24px rgba(102, 82, 218, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.2);
			transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
		}

		[data-testid="stPageLink"] a:hover,
		.stButton > button:hover,
		[data-testid="stFormSubmitButton"] button:hover,
		[data-testid="stDownloadButton"] button:hover {
			transform: translateY(-2px);
			border-color: rgba(210, 203, 255, 0.54);
			filter: brightness(1.12);
			box-shadow: 0 12px 30px rgba(102, 82, 218, 0.32), 0 0 20px rgba(66, 230, 208, 0.12);
			color: #ffffff;
		}

		[data-testid="stSidebar"] [data-testid="stPageLink"] a {
			border-color: rgba(208, 204, 255, 0.12);
			background: rgba(255, 255, 255, 0.035);
			box-shadow: none;
		}

		[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
			border-color: rgba(173, 161, 255, 0.36);
			background: linear-gradient(100deg, rgba(116, 96, 230, 0.28), rgba(39, 185, 163, 0.13));
		}

		[data-testid="stAlert"],
		[data-testid="stToast"] {
			border: 1px solid rgba(204, 203, 255, 0.15);
			border-radius: 14px;
			background: rgba(24, 26, 42, 0.88);
			color: #f2f0ff;
			box-shadow: 0 12px 30px rgba(0, 0, 0, 0.24);
			backdrop-filter: blur(10px);
		}

		.finance-footer {
			border-color: rgba(204, 203, 255, 0.13);
			color: #9293ad;
		}
		</style>
		""",
		unsafe_allow_html=True,
	)


def render_footer() -> None:
	"""Render the shared Mongolian application footer."""
	st.markdown(
		'<div class="finance-footer">Хувийн санхүү · Аюулгүй, найдвартай</div>',
		unsafe_allow_html=True,
	)


def style_plotly_chart(figure):
	"""Apply the shared dark glass and neon palette to a Plotly figure."""
	figure.update_layout(
		template="plotly_dark",
		paper_bgcolor="rgba(0,0,0,0)",
		plot_bgcolor="rgba(0,0,0,0)",
		colorway=["#9b8cff", "#36e2cc", "#55e39f", "#ff789b", "#d88cff"],
		font=dict(family="Aptos, Segoe UI, sans-serif", color="#c4c2da", size=12),
		hoverlabel=dict(
			bgcolor="rgba(24, 25, 42, 0.96)",
			bordercolor="rgba(137, 128, 255, 0.62)",
			font=dict(color="#faf9ff", family="Aptos, Segoe UI, sans-serif"),
		),
		margin=dict(l=12, r=12, t=14, b=12),
	)
	figure.update_xaxes(
		gridcolor="rgba(188, 186, 235, 0.1)",
		linecolor="rgba(188, 186, 235, 0.22)",
		zerolinecolor="rgba(188, 186, 235, 0.18)",
		tickfont=dict(color="#aeadc4"),
	)
	figure.update_yaxes(
		gridcolor="rgba(188, 186, 235, 0.1)",
		linecolor="rgba(188, 186, 235, 0.22)",
		zerolinecolor="rgba(188, 186, 235, 0.18)",
		tickfont=dict(color="#aeadc4"),
	)
	return figure