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

		[data-testid="stTable"] table {
			border-collapse: separate;
			border-spacing: 0;
			color: #f2f0ff;
		}

		[data-testid="stTable"] th {
			border-bottom: 1px solid rgba(204, 203, 255, 0.18);
			background: rgba(49, 45, 78, 0.96);
			color: #ffffff;
			font-weight: 700;
		}

		[data-testid="stTable"] td {
			border-bottom: 1px solid rgba(204, 203, 255, 0.09);
			background: rgba(20, 22, 36, 0.9);
			color: #eeecff;
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

		[data-testid="stTextInput"] input,
		[data-testid="stNumberInput"] input,
		[data-testid="stDateInput"] input,
		[data-testid="stTextArea"] textarea,
		[data-testid="stTimeInput"] input {
			color: #ffffff !important;
			caret-color: #42e6d0;
		}

		[data-testid="stTextInput"] input::placeholder,
		[data-testid="stNumberInput"] input::placeholder,
		[data-testid="stTextArea"] textarea::placeholder {
			color: #aaa9c3 !important;
			opacity: 1;
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

		[data-testid="stFileUploaderDropzoneInstructions"] {
			font-size: 0 !important;
			color: transparent !important;
		}

		[data-testid="stFileUploaderDropzoneInstructions"]::before,
		[data-testid="stFileUploaderDropzoneInstructions"]::after {
			display: block;
			color: #f4f2ff;
			font-size: 0.9rem;
			font-weight: 650;
			line-height: 1.5;
		}

		[data-testid="stFileUploaderDropzoneInstructions"]::before {
			content: "Файлаа энд чирж оруулах эсвэл товчоор сонгоно уу";
		}

		[data-testid="stFileUploaderDropzoneInstructions"]::after {
			margin-top: 0.2rem;
			color: #bcbad2;
			content: "Дэмжих төрөл: XLSX, CSV · Нэг файл 200 МБ хүртэл";
			font-size: 0.76rem;
			font-weight: 500;
		}

		[data-testid="stFileUploaderDropzone"] button {
			min-height: 2.65rem;
			border: 1px solid rgba(194, 185, 255, 0.5);
			border-radius: 10px;
			background: linear-gradient(115deg, #b1a3ff, #c5a1ff 58%, #73ead7);
			color: #151526 !important;
			font-size: 0 !important;
			font-weight: 800;
			box-shadow: 0 6px 20px rgba(124, 103, 242, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.55);
		}

		[data-testid="stFileUploaderDropzone"] button::after {
			content: "Файл сонгох";
			color: #151526;
			font-size: 0.86rem;
			font-weight: 800;
		}

		[data-testid="stFileUploaderDropzone"] button:hover {
			border-color: #ffffff;
			filter: brightness(1.08);
			box-shadow: 0 8px 24px rgba(124, 103, 242, 0.34), 0 0 18px rgba(66, 230, 208, 0.15);
		}

		[data-testid="stDataFrame"],
		[data-testid="stDataEditor"] {
			--gdg-bg-cell: rgba(18, 20, 33, 0.98);
			--gdg-bg-cell-medium: rgba(25, 27, 43, 0.98);
			--gdg-bg-header: rgba(38, 37, 61, 0.99);
			--gdg-bg-header-has-focus: rgba(61, 54, 104, 0.99);
			--gdg-bg-header-hovered: rgba(52, 49, 82, 0.99);
			--gdg-text-dark: #ffffff;
			--gdg-text-medium: #eeecff;
			--gdg-text-light: #c3c1d8;
			--gdg-text-header: #ffffff;
			--gdg-text-header-selected: #ffffff;
			--gdg-border-color: rgba(204, 203, 255, 0.18);
			--gdg-accent-color: #9689ff;
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
	if st.session_state.get("finance_theme_mode") == "Гэгээлэг":
		st.markdown(
			"""
			<style>
			:root {
				color-scheme: light;
				--finance-ink: #202344;
				--finance-muted: #5e6680;
				--finance-border: rgba(75, 80, 134, 0.17);
			}

			[data-testid="stAppViewContainer"] {
				background: linear-gradient(135deg, #f2f3ff 0%, #edf2fb 54%, #e9f8f4 100%);
				color: #202344;
			}

			[data-testid="stHeader"] {
				background: rgba(242, 243, 255, 0.78);
			}

			[data-testid="stSidebar"] {
				border-right-color: rgba(75, 80, 134, 0.15);
				background: linear-gradient(165deg, #f0efff 0%, #eaebf7 58%, #e7f7f2 100%);
				box-shadow: 12px 0 36px rgba(56, 58, 100, 0.08);
			}

			[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
			[data-testid="stSidebar"] [data-testid="stPageLink"] a {
				color: #282943;
			}

			[data-testid="stSidebar"] [data-testid="stPageLink"] a {
				border-color: rgba(75, 80, 134, 0.13);
				background: rgba(255, 255, 255, 0.45);
			}

			[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
				background: linear-gradient(100deg, rgba(121, 99, 223, 0.18), rgba(54, 190, 170, 0.16));
				color: #202344;
			}

			.main h1, .main h2, .main h3 {
				color: #202344;
			}

			.main [data-testid="stCaptionContainer"] {
				color: #5e6680;
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
				border-color: rgba(75, 80, 134, 0.16);
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.88), rgba(239, 240, 252, 0.74));
				box-shadow: 0 16px 36px rgba(55, 58, 96, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.96);
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.97), rgba(235, 232, 255, 0.88));
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.97), rgba(255, 235, 241, 0.88));
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.97), rgba(229, 249, 244, 0.88));
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.97), rgba(246, 235, 255, 0.88));
			}

			[data-testid="stMetricLabel"] {
				color: #4e5672;
			}

			[data-testid="stMetricValue"] {
				color: #202344;
			}

			.st-key-finance-dashboard-kpis [data-testid="stMetric"]::after {
				background: rgba(121, 99, 223, 0.12);
				color: #493da7;
			}

			.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]::after {
				background: rgba(255, 120, 155, 0.15);
				color: #9a3858;
			}

			.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]::after {
				background: rgba(54, 190, 170, 0.16);
				color: #146d61;
			}

			.st-key-finance-dashboard-kpis [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]::after {
				background: rgba(189, 140, 255, 0.16);
				color: #69429c;
			}

			[data-testid="stPlotlyChart"],
			[data-testid="stDataFrame"],
			[data-testid="stDataEditor"],
			[data-testid="stTable"],
			[data-testid="stForm"],
			[data-testid="stVerticalBlockBorderWrapper"] {
				border-color: rgba(75, 80, 134, 0.16);
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.84), rgba(239, 241, 250, 0.74));
				box-shadow: 0 16px 36px rgba(55, 58, 96, 0.09), inset 0 1px 0 rgba(255, 255, 255, 0.96);
			}

			[data-testid="stTextInput"] input,
			[data-testid="stNumberInput"] input,
			[data-testid="stDateInput"] input,
			[data-testid="stTextArea"] textarea,
			[data-testid="stTimeInput"] input,
			[data-baseweb="select"] > div {
				border-color: rgba(75, 80, 134, 0.22);
				background: rgba(255, 255, 255, 0.88);
				color: #202344;
			}

			[data-testid="stTextInput"] input,
			[data-testid="stNumberInput"] input,
			[data-testid="stDateInput"] input,
			[data-testid="stTextArea"] textarea,
			[data-testid="stTimeInput"] input {
				color: #202344 !important;
			}

			[data-testid="stTextInput"] input::placeholder,
			[data-testid="stNumberInput"] input::placeholder,
			[data-testid="stTextArea"] textarea::placeholder {
				color: #6a7089 !important;
			}

			[data-baseweb="popover"] [role="listbox"],
			[data-baseweb="menu"],
			[data-baseweb="popover"] [role="option"] {
				border-color: rgba(75, 80, 134, 0.18);
				background: #ffffff;
				color: #202344;
			}

			[data-baseweb="popover"] [role="option"]:hover,
			[data-baseweb="popover"] [aria-selected="true"] {
				background: linear-gradient(100deg, rgba(121, 99, 223, 0.16), rgba(54, 190, 170, 0.14));
				color: #202344;
			}

			label, [data-testid="stWidgetLabel"] p,
			[data-testid="stCheckbox"] label,
			[data-testid="stRadio"] label,
			[data-testid="stToggle"] label {
				color: #343650;
			}

			[data-testid="stFileUploaderDropzone"] {
				border-color: rgba(98, 83, 196, 0.32);
				background: rgba(255, 255, 255, 0.8);
			}

			[data-testid="stFileUploaderDropzoneInstructions"]::before {
				color: #292747;
			}

			[data-testid="stFileUploaderDropzoneInstructions"]::after {
				color: #5f6680;
			}

			[data-testid="stTable"] th {
				background: rgba(228, 226, 248, 0.96);
				color: #252642;
			}

			[data-testid="stTable"] td {
				background: rgba(255, 255, 255, 0.9);
				color: #292b43;
			}

			[data-testid="stDataFrame"],
			[data-testid="stDataEditor"] {
				--gdg-bg-cell: rgba(255, 255, 255, 0.97);
				--gdg-bg-cell-medium: rgba(245, 245, 252, 0.99);
				--gdg-bg-header: rgba(229, 227, 249, 0.99);
				--gdg-bg-header-has-focus: rgba(207, 200, 248, 0.99);
				--gdg-bg-header-hovered: rgba(218, 215, 246, 0.99);
				--gdg-text-dark: #202344;
				--gdg-text-medium: #424862;
				--gdg-text-light: #626982;
				--gdg-text-header: #252642;
				--gdg-text-header-selected: #252642;
				--gdg-border-color: rgba(83, 87, 143, 0.16);
				--gdg-accent-color: #6557e8;
			}

			[data-testid="stAlert"],
			[data-testid="stToast"] {
				border-color: rgba(83, 87, 143, 0.17);
				background: rgba(255, 255, 255, 0.9);
				color: #252642;
			}

			[data-testid="stAlert"] p,
			[data-testid="stToast"] p {
				color: #252642;
			}

			.finance-footer {
				border-color: rgba(83, 87, 143, 0.16);
				color: #666d86;
			}
			</style>
			""",
			unsafe_allow_html=True,
		)
	if st.session_state.get("finance_theme_mode") == "Гэгээлэг":
		st.markdown(
			"""
			<style>
			:root {
				color-scheme: light;
				--finance-ink: #202344;
				--finance-muted: #646b85;
				--finance-border: rgba(80, 82, 138, 0.16);
			}

			[data-testid="stAppViewContainer"] {
				background-color: #f7f8ff;
				background-image: linear-gradient(135deg, #f6f7ff 0%, #f2f5fb 52%, #edf8f5 100%);
				color: #202344;
			}

			[data-testid="stHeader"] {
				background: rgba(247, 248, 255, 0.8);
			}

			[data-testid="stSidebar"] {
				border-right: 1px solid rgba(86, 82, 155, 0.14);
				background: linear-gradient(165deg, #f4f3ff 0%, #eeeffa 58%, #eaf8f5 100%);
				box-shadow: 12px 0 40px rgba(56, 58, 100, 0.08);
			}

			[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
			[data-testid="stSidebar"] [data-testid="stPageLink"] a {
				color: #292747;
			}

			[data-testid="stSidebar"] [data-testid="stPageLink"] a {
				border-color: rgba(86, 82, 155, 0.12);
				background: rgba(255, 255, 255, 0.48);
			}

			.main h1, .main h2, .main h3 {
				color: #202344;
			}

			.main [data-testid="stCaptionContainer"] {
				color: #646b85;
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
				border-color: rgba(84, 87, 143, 0.15);
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.84), rgba(241, 242, 253, 0.74));
				box-shadow: 0 16px 38px rgba(47, 51, 91, 0.09), inset 0 1px 0 rgba(255, 255, 255, 0.92);
				backdrop-filter: blur(12px);
				-webkit-backdrop-filter: blur(12px);
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(237, 234, 255, 0.86));
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(255, 237, 242, 0.86));
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(231, 249, 246, 0.86));
			}

			[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(246, 238, 255, 0.86));
			}

			[data-testid="stMetricLabel"] {
				color: #535a75;
			}

			[data-testid="stMetricValue"] {
				color: #202344;
				text-shadow: 0 0 18px rgba(114, 99, 223, 0.12);
			}

			[data-testid="stPlotlyChart"],
			[data-testid="stDataFrame"],
			[data-testid="stDataEditor"],
			[data-testid="stTable"],
			[data-testid="stForm"],
			[data-testid="stVerticalBlockBorderWrapper"] {
				border-color: rgba(83, 87, 143, 0.15);
				background: linear-gradient(145deg, rgba(255, 255, 255, 0.82), rgba(239, 241, 250, 0.72));
				box-shadow: 0 16px 38px rgba(47, 51, 91, 0.085), inset 0 1px 0 rgba(255, 255, 255, 0.94);
			}

			[data-testid="stPlotlyChart"] {
				background: rgba(247, 248, 255, 0.7);
			}

			[data-testid="stTextInput"] input,
			[data-testid="stNumberInput"] input,
			[data-testid="stDateInput"] input,
			[data-testid="stTextArea"] textarea,
			[data-testid="stTimeInput"] input,
			[data-baseweb="select"] > div {
				border-color: rgba(83, 87, 143, 0.2);
				background: rgba(255, 255, 255, 0.82);
				color: #202344;
				box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.95);
			}

			[data-testid="stTextInput"] input,
			[data-testid="stNumberInput"] input,
			[data-testid="stDateInput"] input,
			[data-testid="stTextArea"] textarea,
			[data-testid="stTimeInput"] input {
				color: #202344 !important;
			}

			[data-testid="stTextInput"] input::placeholder,
			[data-testid="stTextArea"] textarea::placeholder {
				color: #666d86 !important;
			}

			[data-baseweb="popover"] [role="listbox"],
			[data-baseweb="menu"],
			[data-baseweb="popover"] [role="option"] {
				border-color: rgba(83, 87, 143, 0.18);
				background: #ffffff;
				color: #202344;
			}

			[data-baseweb="popover"] [role="option"]:hover,
			[data-baseweb="popover"] [aria-selected="true"] {
				background: linear-gradient(100deg, rgba(121, 99, 223, 0.16), rgba(54, 190, 170, 0.14));
				color: #202344;
			}

			label, [data-testid="stWidgetLabel"] p,
			[data-testid="stCheckbox"] label,
			[data-testid="stRadio"] label,
			[data-testid="stToggle"] label {
				color: #343650;
			}

			[data-testid="stFileUploaderDropzone"] {
				border-color: rgba(98, 83, 196, 0.32);
				background: rgba(255, 255, 255, 0.78);
			}

			[data-testid="stFileUploaderDropzoneInstructions"]::before {
				color: #292747;
			}

			[data-testid="stFileUploaderDropzoneInstructions"]::after {
				color: #5f6680;
			}

			[data-testid="stTable"] th {
				background: rgba(228, 226, 248, 0.96);
				color: #252642;
			}

			[data-testid="stTable"] td {
				background: rgba(255, 255, 255, 0.86);
				color: #292b43;
			}

			[data-testid="stDataFrame"],
			[data-testid="stDataEditor"] {
				--gdg-bg-cell: rgba(255, 255, 255, 0.96);
				--gdg-bg-cell-medium: rgba(244, 244, 252, 0.98);
				--gdg-bg-header: rgba(229, 227, 249, 0.99);
				--gdg-bg-header-has-focus: rgba(207, 200, 248, 0.99);
				--gdg-bg-header-hovered: rgba(218, 215, 246, 0.99);
				--gdg-text-dark: #202344;
				--gdg-text-medium: #424862;
				--gdg-text-light: #626982;
				--gdg-text-header: #252642;
				--gdg-text-header-selected: #252642;
				--gdg-border-color: rgba(83, 87, 143, 0.16);
				--gdg-accent-color: #6557e8;
			}

			[data-testid="stAlert"],
			[data-testid="stToast"] {
				border-color: rgba(83, 87, 143, 0.17);
				background: rgba(255, 255, 255, 0.88);
				color: #252642;
			}

			[data-testid="stAlert"] p,
			[data-testid="stToast"] p {
				color: #252642;
			}

			.finance-footer {
				border-color: rgba(83, 87, 143, 0.16);
				color: #666d86;
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
	if st.session_state.get("finance_theme_mode") == "Гэгээлэг":
		figure.update_layout(
			template="plotly_white",
			paper_bgcolor="rgba(0,0,0,0)",
			plot_bgcolor="rgba(255,255,255,0.12)",
			colorway=["#5b4de1", "#008f80", "#13834d", "#d84d78", "#8c4bce"],
			font=dict(family="Aptos, Segoe UI, sans-serif", color="#424862", size=12),
			hoverlabel=dict(
				bgcolor="rgba(255,255,255,0.98)",
				bordercolor="rgba(91,77,225,0.4)",
				font=dict(color="#202344", family="Aptos, Segoe UI, sans-serif"),
			),
			margin=dict(l=12, r=12, t=14, b=12),
		)
		figure.update_xaxes(
			gridcolor="rgba(78,84,128,0.12)",
			linecolor="rgba(78,84,128,0.24)",
			zerolinecolor="rgba(78,84,128,0.2)",
			tickfont=dict(color="#555d78"),
		)
		figure.update_yaxes(
			gridcolor="rgba(78,84,128,0.12)",
			linecolor="rgba(78,84,128,0.24)",
			zerolinecolor="rgba(78,84,128,0.2)",
			tickfont=dict(color="#555d78"),
		)
		return figure

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

def render_lang_toggle(location: str = "sidebar") -> str:
    """Simple language toggle."""
    try:
        import streamlit as st
    except Exception:
        return "mn"
    if not hasattr(st, "session_state"):
        return "mn"
    if "lang" not in st.session_state:
        st.session_state["lang"] = "mn"
    lang = st.session_state["lang"]
    try:
        if location in ("sidebar", "side", "left"):
            with st.sidebar:
                st.markdown("**Хэл / Language**")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("MN", use_container_width=True, type="primary" if lang == "mn" else "secondary", key="lt_mn_sb"):
                        st.session_state["lang"] = "mn"
                        st.rerun()
                with c2:
                    if st.button("EN", use_container_width=True, type="primary" if lang == "en" else "secondary", key="lt_en_sb"):
                        st.session_state["lang"] = "en"
                        st.rerun()
            return st.session_state["lang"]
    except Exception:
        pass
    try:
        c1, c2, c3 = st.columns([8, 1, 1])
        with c2:
            if st.button("MN", use_container_width=True, type="primary" if st.session_state.get("lang") == "mn" else "secondary", key="lt_mn_top"):
                st.session_state["lang"] = "mn"
                st.rerun()
        with c3:
            if st.button("EN", use_container_width=True, type="primary" if st.session_state.get("lang") == "en" else "secondary", key="lt_en_top"):
                st.session_state["lang"] = "en"
                st.rerun()
    except Exception:
        pass
    return st.session_state.get("lang", "mn")
