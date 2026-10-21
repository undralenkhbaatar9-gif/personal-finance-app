import streamlit as st


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