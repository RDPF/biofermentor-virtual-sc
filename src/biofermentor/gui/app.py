"""Optional rich Tkinter/Matplotlib interface for Biofermentor Virtual SC v3.0.0.

This module is intentionally isolated from biofermentor.core. Headless use,
pytest and CI never import this file.
"""
import csv
import json
import logging
import traceback
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from biofermentor.core import (
    defaults, BiofermentorSimulator, SCProcess, SimulationCancelled
)
from biofermentor.core.utils import EPS

APP_TITLE = "Biofermentor Virtual SC v3.0.0 — Scientific Metabolism & Reproducible Validation"
LOG = logging.getLogger(__name__)

def fnum(x, default=0.0):
    try:
        return float(str(x).strip().replace(",", "."))
    except Exception:
        return float(default)

def fmt(v, nd=3):
    try:
        return f"{float(v):.{nd}f}"
    except Exception:
        return str(v)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)

        # Fit comfortably on notebook screens while still scaling up on large
        # displays.  The old fixed 1580x940 geometry could exceed 1366x768.
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        width = min(1500, max(1040, sw - 70))
        height = min(900, max(650, sh - 95))
        width = min(width, sw)
        height = min(height, sh)
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(min(1080, max(920, sw - 40)), min(680, max(620, sh - 70)))

        self.p = defaults()
        self.vars = {}
        self.sensor_fault_vars = {}
        self.act_fault_vars = {}
        self.result = None
        self.worker_thread = None
        self.worker_queue = queue.Queue()
        self.cancel_event = threading.Event()

        self._style()
        self._ui()
        self._configure_shortcuts()
        self.load_defaults()
        self.after_idle(self._set_initial_sash)

    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass

        # Neutral scientific/HMI palette.  Everything remains native Tk/ttk,
        # preserving portability and PyInstaller friendliness.
        bg = "#eef2f5"
        panel = "#f7f9fb"
        navy = "#15324a"
        blue = "#1f5f8f"
        blue_hover = "#174a70"
        ink = "#1c2d3d"
        muted = "#667788"

        self.configure(background=bg)
        s.configure(".", font=("TkDefaultFont", 9), background=bg, foreground=ink)
        s.configure("Header.TFrame", background=navy)
        s.configure("HeaderTitle.TLabel", background=navy, foreground="#ffffff", font=("TkDefaultFont", 16, "bold"))
        s.configure("HeaderSub.TLabel", background=navy, foreground="#cbd9e5", font=("TkDefaultFont", 9))
        s.configure("HeaderBadge.TLabel", background=navy, foreground="#d8e8f5", font=("TkDefaultFont", 9, "bold"))
        s.configure("Toolbar.TFrame", background="#e3e9ee")
        s.configure("Sidebar.TFrame", background="#e9eef2")
        s.configure("Content.TFrame", background=panel)
        s.configure("SidebarTitle.TLabel", background="#e9eef2", foreground=navy, font=("TkDefaultFont", 11, "bold"))
        s.configure("SidebarSub.TLabel", background="#e9eef2", foreground=muted, font=("TkDefaultFont", 8))

        s.configure("TButton", padding=(10, 6))
        s.configure("Primary.TButton", font=("TkDefaultFont", 10, "bold"), padding=(16, 7), background=blue, foreground="#ffffff", borderwidth=0)
        s.map("Primary.TButton", background=[("active", blue_hover), ("pressed", blue_hover), ("disabled", "#9aabb9")], foreground=[("disabled", "#e6ebef")])
        s.configure("Danger.TButton", font=("TkDefaultFont", 9, "bold"), padding=(12, 7), background="#a94747", foreground="#ffffff")
        s.map("Danger.TButton", background=[("active", "#873737"), ("disabled", "#c7cdd2")], foreground=[("disabled", "#f4f4f4")])
        s.configure("Secondary.TButton", padding=(10, 6), background="#f8fafb")

        s.configure("Group.TLabelframe", background="#f7f9fb", borderwidth=1, relief="solid")
        s.configure("Group.TLabelframe.Label", background="#f7f9fb", foreground=navy, font=("TkDefaultFont", 9, "bold"))
        s.configure("TEntry", padding=(5, 4))
        s.configure("TCombobox", padding=(4, 3))
        s.configure("TNotebook", background=panel, borderwidth=0)
        s.configure("TNotebook.Tab", padding=(10, 6), font=("TkDefaultFont", 9))
        s.map("TNotebook.Tab", background=[("selected", "#ffffff"), ("active", "#e5edf4")], foreground=[("selected", navy)])
        s.configure("Status.TLabel", background=bg, foreground=muted)
        s.configure("Treeview", rowheight=27, background="#ffffff", fieldbackground="#ffffff", borderwidth=0)
        s.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"), background="#dfe7ee", foreground=navy, padding=(5, 6))
        s.map("Treeview", background=[("selected", "#d9eaf7")], foreground=[("selected", ink)])

    def _ui(self):
        # ------------------------------------------------------------------
        # Brand header: separated from the action toolbar to prevent the
        # cramped single-row appearance seen on notebook resolutions.
        # ------------------------------------------------------------------
        header = ttk.Frame(self, style="Header.TFrame", padding=(14, 9))
        header.pack(fill="x")
        brand = ttk.Frame(header, style="Header.TFrame")
        brand.pack(side="left", fill="x", expand=True)
        ttk.Label(brand, text="Biofermentor Virtual SC v3.0.0", style="HeaderTitle.TLabel").pack(anchor="w")
        ttk.Label(
            brand,
            text="Planta virtual de fermentação alcoólica • Saccharomyces cerevisiae",
            style="HeaderSub.TLabel",
        ).pack(anchor="w", pady=(1, 0))
        ttk.Label(header, text="SCIENTIFIC BUILD", style="HeaderBadge.TLabel").pack(side="right", padx=(12, 2))

        toolbar = ttk.Frame(self, style="Toolbar.TFrame", padding=(10, 5))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Padrões", command=self.load_defaults, style="Secondary.TButton").pack(side="left", padx=(0, 4))
        ttk.Button(toolbar, text="Abrir receita", command=self.load_json, style="Secondary.TButton").pack(side="left", padx=4)
        ttk.Button(toolbar, text="Salvar receita", command=self.save_json, style="Secondary.TButton").pack(side="left", padx=4)
        ttk.Button(toolbar, text="Exportar CSV", command=self.export_csv, style="Secondary.TButton").pack(side="left", padx=4)

        self.run_button = ttk.Button(toolbar, text="SIMULAR", command=self.run_sim, style="Primary.TButton")
        self.run_button.pack(side="right", padx=(6, 0))
        self.cancel_button = ttk.Button(toolbar, text="CANCELAR", command=self.cancel_sim, state="disabled", style="Danger.TButton")
        self.cancel_button.pack(side="right", padx=4)

        # ------------------------------------------------------------------
        # Main workspace
        # ------------------------------------------------------------------
        self.main_pane = ttk.Panedwindow(self, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True, padx=8, pady=8)
        left = ttk.Frame(self.main_pane, style="Sidebar.TFrame")
        right = ttk.Frame(self.main_pane, style="Content.TFrame")
        self.main_pane.add(left, weight=0)
        self.main_pane.add(right, weight=1)

        side_head = ttk.Frame(left, style="Sidebar.TFrame", padding=(8, 6, 8, 4))
        side_head.pack(fill="x")
        ttk.Label(side_head, text="Parâmetros do processo", style="SidebarTitle.TLabel").pack(anchor="w")
        ttk.Label(side_head, text="Receita, controles, falhas e limites operacionais", style="SidebarSub.TLabel").pack(anchor="w", pady=(1, 0))

        params_host = ttk.Frame(left, style="Sidebar.TFrame")
        params_host.pack(fill="both", expand=True)
        self.params_canvas = tk.Canvas(params_host, width=350, highlightthickness=0, bd=0, bg="#e9eef2")
        sb = ttk.Scrollbar(params_host, orient="vertical", command=self.params_canvas.yview)
        self.pframe = ttk.Frame(self.params_canvas, style="Sidebar.TFrame")
        self.params_window = self.params_canvas.create_window((0, 0), window=self.pframe, anchor="nw")
        self.pframe.bind("<Configure>", lambda e: self.params_canvas.configure(scrollregion=self.params_canvas.bbox("all")))
        self.params_canvas.bind("<Configure>", self._resize_params_window)
        self.params_canvas.configure(yscrollcommand=sb.set)
        self.params_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.params_canvas.bind("<Enter>", self._bind_params_wheel)
        self.params_canvas.bind("<Leave>", self._unbind_params_wheel)
        self._params_ui()

        self.nb = ttk.Notebook(right)
        self.nb.pack(fill="both", expand=True)
        self.tabs = {}
        for key, title in [
            ("pid", "P&ID / Operação"), ("overview", "Visão geral"), ("bio", "Bioprocesso"),
            ("gas", "Gases / OUR-CER"), ("ctrl", "Atuadores"), ("kin", "Cinética"),
            ("recipe", "Receita"), ("alarms", "Alarmes"), ("metrics", "Métricas")
        ]:
            self.tabs[key] = ttk.Frame(self.nb, style="Content.TFrame")
            self.nb.add(self.tabs[key], text=title)

        self._pid_ui()
        self.fig_over, self.can_over = self._figure(self.tabs["overview"])
        self.fig_bio, self.can_bio = self._figure(self.tabs["bio"])
        self.fig_gas, self.can_gas = self._figure(self.tabs["gas"])
        self.fig_ctrl, self.can_ctrl = self._figure(self.tabs["ctrl"])
        self.fig_kin, self.can_kin = self._figure(self.tabs["kin"])
        self._recipe_ui()
        self._alarms_ui()
        self._metrics_ui()

        # Persistent status bar.  Critical alarms are deliberately not placed
        # here; TRIP status is shown prominently inside the process view.
        bottom = ttk.Frame(self, padding=(9, 2, 9, 6))
        bottom.pack(fill="x")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(bottom, maximum=100.0, variable=self.progress_var, length=230)
        self.progress.pack(side="right", padx=(10, 0))
        self.status = ttk.Label(bottom, text="Pronto.", anchor="w", style="Status.TLabel")
        self.status.pack(side="left", fill="x", expand=True)

    def _figure(self, parent):
        host = ttk.Frame(parent, style="Content.TFrame", padding=7)
        host.pack(fill="both", expand=True)
        fig = Figure(figsize=(8, 6), dpi=100, facecolor="#ffffff")
        cv = FigureCanvasTkAgg(fig, master=host)
        cv.draw()
        widget = cv.get_tk_widget()
        widget.configure(bg="#ffffff", highlightthickness=0)
        widget.pack(fill="both", expand=True)
        tb = NavigationToolbar2Tk(cv, host, pack_toolbar=False)
        tb.update()
        tb.pack(fill="x", pady=(4, 0))
        return fig, cv

    def _set_initial_sash(self):
        try:
            total = self.main_pane.winfo_width()
            target = max(330, min(380, int(total * 0.28)))
            self.main_pane.sashpos(0, target)
        except tk.TclError:
            pass

    def _resize_params_window(self, event):
        try:
            self.params_canvas.itemconfigure(self.params_window, width=max(260, event.width - 2))
        except tk.TclError:
            pass

    def _bind_params_wheel(self, _event=None):
        self.bind_all("<MouseWheel>", self._on_params_wheel)
        self.bind_all("<Button-4>", self._on_params_wheel)
        self.bind_all("<Button-5>", self._on_params_wheel)

    def _unbind_params_wheel(self, _event=None):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_params_wheel(self, event):
        if getattr(event, "num", None) == 4:
            delta = -2
        elif getattr(event, "num", None) == 5:
            delta = 2
        else:
            delta = -int(event.delta / 120) if event.delta else 0
        if delta:
            self.params_canvas.yview_scroll(delta, "units")
        return "break"

    def _configure_shortcuts(self):
        self.bind("<Control-Return>", lambda _e: self.run_sim())
        self.bind("<Control-s>", lambda _e: self.save_json())
        self.bind("<Control-o>", lambda _e: self.load_json())
        self.bind("<Control-e>", lambda _e: self.export_csv())
        self.bind("<Escape>", lambda _e: self.cancel_sim())

    def _alarms_ui(self):
        host = ttk.Frame(self.tabs["alarms"], style="Content.TFrame", padding=10)
        host.pack(fill="both", expand=True)
        ttk.Label(host, text="Eventos e intertravamentos", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        ttk.Label(host, text="Histórico gerado pela última simulação", foreground="#667788").pack(anchor="w", pady=(0, 8))

        self.alarm_status_var = tk.StringVar(value="Nenhuma simulação executada")
        self.alarm_status = tk.Label(
            host, textvariable=self.alarm_status_var, anchor="w",
            padx=10, pady=7, bg="#e8eef3", fg="#29445c",
            font=("TkDefaultFont", 9, "bold"), bd=0,
        )
        self.alarm_status.pack(fill="x", pady=(0, 8))

        tree_host = ttk.Frame(host)
        tree_host.pack(fill="both", expand=True)
        self.alarm_tree = ttk.Treeview(tree_host, columns=("time", "level", "event"), show="headings")
        self.alarm_tree.heading("time", text="Tempo [h]")
        self.alarm_tree.heading("level", text="Nível")
        self.alarm_tree.heading("event", text="Evento")
        self.alarm_tree.column("time", width=110, minwidth=90, anchor="e", stretch=False)
        self.alarm_tree.column("level", width=100, minwidth=80, anchor="center", stretch=False)
        self.alarm_tree.column("event", width=520, minwidth=280, anchor="w", stretch=True)
        ysb = ttk.Scrollbar(tree_host, orient="vertical", command=self.alarm_tree.yview)
        xsb = ttk.Scrollbar(tree_host, orient="horizontal", command=self.alarm_tree.xview)
        self.alarm_tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.alarm_tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        tree_host.rowconfigure(0, weight=1)
        tree_host.columnconfigure(0, weight=1)
        self.alarm_tree.tag_configure("WARN", background="#fff7df")
        self.alarm_tree.tag_configure("ALARM", background="#ffe7df")
        self.alarm_tree.tag_configure("TRIP", background="#ffdede")

    def _metrics_ui(self):
        host = ttk.Frame(self.tabs["metrics"], style="Content.TFrame", padding=10)
        host.pack(fill="both", expand=True)
        ttk.Label(host, text="Relatório da batelada", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        ttk.Label(host, text="Desempenho, segurança e integridade científica", foreground="#667788").pack(anchor="w", pady=(0, 7))
        text_host = ttk.Frame(host)
        text_host.pack(fill="both", expand=True)
        self.metric_text = tk.Text(
            text_host, font=("Courier New", 10), wrap="word",
            bg="#ffffff", fg="#203140", bd=0, padx=12, pady=10,
            insertbackground="#203140",
        )
        msb = ttk.Scrollbar(text_host, orient="vertical", command=self.metric_text.yview)
        self.metric_text.configure(yscrollcommand=msb.set)
        self.metric_text.pack(side="left", fill="both", expand=True)
        msb.pack(side="right", fill="y")

    def _var(self,k,boolv=False):
        v=tk.BooleanVar() if boolv else tk.StringVar()
        self.vars[k]=v; return v

    def _section(self,title):
        f=ttk.Labelframe(self.pframe,text=title,style="Group.TLabelframe",padding=5)
        f.pack(fill="x",padx=5,pady=4); f.columnconfigure(1,weight=1); return f

    def _entry(self,f,r,label,k):
        ttk.Label(f,text=label).grid(row=r,column=0,sticky="w",padx=3,pady=1)
        ttk.Entry(f,textvariable=self._var(k),width=16).grid(row=r,column=1,sticky="ew",padx=3,pady=1)

    def _combo(self,f,r,label,k,vals):
        ttk.Label(f,text=label).grid(row=r,column=0,sticky="w",padx=3,pady=1)
        ttk.Combobox(f,textvariable=self._var(k),values=vals,state="readonly",width=24).grid(row=r,column=1,sticky="ew",padx=3,pady=1)

    def _check(self,f,r,label,k):
        ttk.Checkbutton(f,text=label,variable=self._var(k,True)).grid(row=r,column=0,columnspan=2,sticky="w",padx=3,pady=1)

    def _params_ui(self):
        f=self._section("Operação")
        self._combo(f,0,"Modo","mode",["Batelada","Fed-batch"])
        for r,(lab,k) in enumerate([("Tempo [h]","tf"),("dt RK4 [h]","dt"),("Seed","seed"),("V máx [L]","Vmax")],1): self._entry(f,r,lab,k)

        f=self._section("Condições iniciais")
        arr=[("Xv [g/L]","Xv0"),("Xd [g/L]","Xd0"),("S [g/L]","S0"),("P [g/L]","P0"),
             ("N [g/L]","N0"),("DO [mg/L]","CL0"),("V [L]","V0"),("T [°C]","T0"),
             ("pH","pH0"),("Espuma","Foam0"),("Pressão [bar g]","Pr0")]
        for r,(lab,k) in enumerate(arr): self._entry(f,r,lab,k)

        f=self._section("Fed-batch")
        self._combo(f,0,"Estratégia","feed_strategy",["Constante","Rampa linear","Exponencial","S-stat (PID)"])
        arr=[("Início [h]","feed_start"),("F0 [L/h]","F0"),("Rampa [L/h²]","F_slope"),
             ("μ feed [1/h]","feed_mu"),("F máx [L/h]","F_max"),("S feed [g/L]","Sfeed"),
             ("N feed [g/L]","Nfeed"),("S SP [g/L]","S_sp"),("Kp S","S_kp"),("Ki S","S_ki")]
        for r,(lab,k) in enumerate(arr,1): self._entry(f,r,lab,k)

        f=self._section("Cinética")
        arr=[("μmax [1/h]","mu_max"),("Ks","Ks"),("KiS","KiS"),("Kn","Kn"),("Ko","Ko"),
             ("Pmax [g/L]","Pmax"),("nP","nP"),("crescimento anaer.","anaer_growth_frac"),
             ("T ótima","Topt"),("largura T","Twidth"),("pH ótimo","pHopt"),("largura pH","pHwidth"),
             ("kd0","kd0"),("peso morte etanol","kd_eth"),("kd máx","kd_max"),("lise","klysis")]
        for r,(lab,k) in enumerate(arr): self._entry(f,r,lab,k)

        f=self._section("Metabolismo v3.0")
        arr=[("Yx/s","Yxs"),("Yp/s ferm.","Yps"),("Yx/N","Yxn"),("manutenção ms","ms"),
             ("qS NG máx [g/g/h]","qS_ng_max"),("Ks cat [g/L]","Ks_cat"),
             ("Kn cat [g/L]","Kn_cat"),("piso cat. em N=0","N_cat_floor"),
             ("exp. desacoplamento N","N_uncouple_exp"),("Kn stress [g/L]","Kn_stress"),
             ("K Crabtree","Kcrab"),("φ ferm. mín","phi_min"),("peso Crabtree","w_crab"),
             ("qP cons máx","qP_cons_max")]
        for r,(lab,k) in enumerate(arr): self._entry(f,r,lab,k)

        f=self._section("DO / gás / agitação")
        self._combo(f,0,"Estratégia DO","DO_strategy",["Fixo","PID agitação","Sequencial RPM → gás → O₂"])
        arr=[("DO SP [%]","DO_sp"),("Kp DO","DO_kp"),("Ki DO","DO_ki"),
             ("RPM base","rpm_base"),("RPM min","rpm_min"),("RPM max","rpm_max"),
             ("Gás base [vvm]","gas_base"),("Gás máx [vvm]","gas_max"),
             ("O2 máx fração","o2_max"),("kLa ref [1/h]","kla_ref"),("C* ref [mg/L]","Cstar_ref"),("coef T C* [1/°C]","Cstar_temp_coeff")]
        for r,(lab,k) in enumerate(arr,1): self._entry(f,r,lab,k)

        f=self._section("Temperatura")
        self._check(f,0,"Controle de T","control_T")
        for r,(lab,k) in enumerate([("T SP","T_sp"),("Kp","T_kp"),("Ki","T_ki"),("Kd","T_kd"),
                                    ("T ambiente","Tamb"),("Potência térmica","Qctrl_max"),
                                    ("ΔH O2 [kJ/mol]","deltaH_O2_kJ_mol"),("ρCp [kJ/L/K]","rhoCp_kJ_L_K")],1): self._entry(f,r,lab,k)

        f=self._section("pH split-range")
        self._check(f,0,"Controle de pH","control_pH")
        for r,(lab,k) in enumerate([("pH SP","pH_sp"),("Kp","pH_kp"),("Ki","pH_ki"),("Kd","pH_kd"),
                                    ("ganho ácido [eq/L/h]","acid_gain"),("ganho base [eq/L/h]","base_gain"),
                                    ("capacidade tampão","buffer_capacity_eq_L_pH"),("ácido metabólico","metabolic_acid_eq_per_g_ethanol")],1): self._entry(f,r,lab,k)

        f=self._section("Espuma")
        self._check(f,0,"Controle antiespumante","foam_control")
        for r,(lab,k) in enumerate([("Liga","foam_on"),("Desliga","foam_off"),("Geração","foam_gen"),
                                    ("Peso gás","foam_gas"),("Decaimento","foam_decay")],1): self._entry(f,r,lab,k)

        f=self._section("Pressão")
        self._check(f,0,"Controle de pressão","pressure_control")
        for r,(lab,k) in enumerate([("SP [bar g]","Pr_sp"),("Kp","Pr_kp"),("Ki","Pr_ki"),
                                    ("Alarme H","Pr_H"),("Trip HH","Pr_HH")],1): self._entry(f,r,lab,k)

        f=self._section("Falhas de sensores")
        for r,k in enumerate(["T","pH","DO","Pr","Xv","S","P"]):
            ttk.Label(f,text=k).grid(row=r,column=0,sticky="w",padx=3,pady=1)
            v=tk.StringVar(value="Normal"); self.sensor_fault_vars[k]=v
            ttk.Combobox(f,textvariable=v,values=["Normal","Bias+","Bias-","Travado","Ruído alto","Zero"],
                         state="readonly",width=18).grid(row=r,column=1,sticky="ew",padx=3,pady=1)

        f=self._section("Falhas de atuadores")
        for r,k in enumerate(["feed","acid","base","antifoam","rpm","gas","o2frac","vent","heat"]):
            ttk.Label(f,text=k).grid(row=r,column=0,sticky="w",padx=3,pady=1)
            v=tk.StringVar(value="Normal"); self.act_fault_vars[k]=v
            ttk.Combobox(f,textvariable=v,values=["Normal","Travado","0%","50%","100%"],
                         state="readonly",width=18).grid(row=r,column=1,sticky="ew",padx=3,pady=1)

    def _pid_ui(self):
        self.pid_canvas = tk.Canvas(
            self.tabs["pid"], bg="#f5f7f9", highlightthickness=0, bd=0,
        )
        self.pid_canvas.pack(fill="both", expand=True, padx=6, pady=6)
        self.pid_canvas.bind("<Configure>", lambda _e: self.draw_pid())

    def draw_pid(self):
        """Responsive vector process view for the virtual fermentor.

        Coordinates are derived from the *actual* canvas dimensions; nothing
        assumes a hidden 680-pixel minimum.  This prevents TRIP banners and
        other critical information from being clipped on 1366x768 notebooks
        or under Windows display scaling.
        """
        c = self.pid_canvas
        c.delete("all")
        w = max(1, c.winfo_width())
        h = max(1, c.winfo_height())
        if w < 320 or h < 260:
            return

        # Palette
        bg = "#f5f7f9"
        card = "#ffffff"
        ink = "#17324d"
        muted = "#6b7b89"
        edge = "#53616e"
        steel = "#cbd3da"
        steel_light = "#edf1f4"
        steel_dark = "#78848f"
        liquid = "#cfe8fb"
        liquid_edge = "#6db2e6"
        pipe = "#245b88"
        gas = "#2f7d4b"
        acid = "#a44848"
        base = "#6549a8"
        anti = "#b87508"

        pad = max(10, int(min(w, h) * 0.018))
        c.create_rectangle(0, 0, w, h, fill=bg, outline="")

        # Title/status area
        title_y = pad + 7
        c.create_text(pad + 8, title_y, anchor="nw", text="V-101 • Fermentador virtual",
                      fill=ink, font=("TkDefaultFont", 13, "bold"))
        c.create_text(pad + 8, title_y + 24, anchor="nw",
                      text="Fermentação alcoólica — Saccharomyces cerevisiae",
                      fill=muted, font=("TkDefaultFont", 9))

        trip = bool(self.result is not None and self.result.get("trip"))
        alarm_count = len(self.result.get("alarms", [])) if self.result is not None else 0
        if trip:
            badge_text, badge_bg, badge_fg = "TRIP ATIVO", "#a92d2d", "#ffffff"
        elif self.result is None:
            badge_text, badge_bg, badge_fg = "PRONTO", "#dbe7ef", ink
        elif alarm_count:
            badge_text, badge_bg, badge_fg = f"{alarm_count} ALARME(S)", "#f3dfad", "#704d00"
        else:
            badge_text, badge_bg, badge_fg = "OPERAÇÃO NORMAL", "#d7eadc", "#245b36"

        badge_w = min(160, max(108, int(w * 0.14)))
        bx1 = w - pad - 8
        bx0 = bx1 - badge_w
        by0, by1 = pad + 6, pad + 36
        c.create_rectangle(bx0, by0, bx1, by1, fill=badge_bg, outline="")
        c.create_text((bx0 + bx1) / 2, (by0 + by1) / 2, text=badge_text,
                      fill=badge_fg, font=("TkDefaultFont", 9, "bold"))

        # Critical TRIP information is always placed immediately below the
        # title and inside the visible canvas, never below the summary panel.
        trip_banner_h = 48 if trip else 0
        if trip:
            ty0 = pad + 52
            ty1 = ty0 + trip_banner_h
            c.create_rectangle(pad + 6, ty0, w - pad - 6, ty1,
                               fill="#fde1e1", outline="#c43e3e", width=2)
            c.create_text(pad + 20, (ty0 + ty1) / 2, anchor="w", text="TRIP",
                          fill="#a42020", font=("TkDefaultFont", 11, "bold"))
            reason = str(self.result.get("trip_reason", "Intertravamento ativo"))
            c.create_text(pad + 82, (ty0 + ty1) / 2, anchor="w", text=reason,
                          fill="#7c2525", font=("TkDefaultFont", 9),
                          width=max(160, w - 2 * pad - 120))

        content_top = pad + 58 + (trip_banner_h + 10 if trip else 0)
        content_bottom = h - pad - 8
        content_h = max(170, content_bottom - content_top)

        # Right live-data card.  Width is responsive but bounded.
        panel_w = int(max(185, min(232, w * 0.225)))
        panel_x1 = w - pad - 6
        panel_x0 = panel_x1 - panel_w
        process_x0 = pad + 6
        process_x1 = panel_x0 - 14
        process_w = max(360, process_x1 - process_x0)

        # Panel card
        py0 = content_top
        py1 = content_bottom
        c.create_rectangle(panel_x0, py0, panel_x1, py1, fill=card,
                           outline="#a6b5c2", width=1)
        c.create_rectangle(panel_x0, py0, panel_x1, py0 + 38, fill="#e8eef4",
                           outline="#a6b5c2", width=1)
        c.create_text(panel_x0 + 12, py0 + 19, anchor="w", text="Resumo online",
                      fill=ink, font=("TkDefaultFont", 10, "bold"))

        vals = {}
        if self.result is not None:
            Y = self.result["Y"][-1]
            M = self.result["M"][-1]
            U = self.result["U"][-1]
            A = self.result["A"][-1]
            vals = {
                "Xv": Y[0], "S": Y[2], "EtOH": Y[3], "N": Y[4], "V": Y[6],
                "T": M[0], "pH": M[1], "DO": M[2], "Pr": M[3],
                "Stress N": A[18], "Foam": M[8], "RPM": U[4], "Gás": U[5],
            }
        items = [
            ("Xv", "g/L"), ("S", "g/L"), ("EtOH", "g/L"), ("N", "g/L"),
            ("Stress N", ""), ("V", "L"), ("T", "°C"), ("pH", ""),
            ("DO", "%"), ("Pr", "bar(g)"), ("Foam", ""), ("RPM", "rpm"), ("Gás", "vvm"),
        ]
        available_rows_h = max(120, py1 - (py0 + 44))
        row_h = max(21, min(30, int(available_rows_h / len(items))))
        ry = py0 + 48 + row_h / 2
        for name, unit in items:
            val = vals.get(name, "—")
            sval = fmt(val, 2) if val != "—" else "—"
            c.create_text(panel_x0 + 12, ry, anchor="w", text=name,
                          fill=ink, font=("TkDefaultFont", 9, "bold"))
            right_text = f"{sval} {unit}".rstrip()
            c.create_text(panel_x1 - 12, ry, anchor="e", text=right_text,
                          fill="#334756", font=("TkDefaultFont", 8))
            c.create_line(panel_x0 + 10, ry + row_h / 2 - 1,
                          panel_x1 - 10, ry + row_h / 2 - 1,
                          fill="#e7ebef")
            ry += row_h

        # Process vessel dimensions derived from available process area.
        vessel_r = int(max(92, min(145, process_w * 0.19)))
        vessel_top = content_top + int(max(46, content_h * 0.10))
        vessel_bottom = content_bottom - int(max(72, content_h * 0.12))
        if vessel_bottom - vessel_top < 210:
            vessel_top = content_top + 36
            vessel_bottom = content_bottom - 56
        vessel_h = vessel_bottom - vessel_top
        cx = process_x0 + int(process_w * 0.56)
        # Keep enough space for left-side stream labels and right instruments.
        cx = max(process_x0 + vessel_r + 180, cx)
        cx = min(process_x1 - vessel_r - 68, cx)
        vl = cx - vessel_r
        vr = cx + vessel_r
        head_h = max(20, int(vessel_r * 0.22))

        # Shadow and support legs
        c.create_oval(vl - 22, vessel_bottom + 44, vr + 22, vessel_bottom + 67,
                      fill="#d9dee3", outline="")
        leg_bottom = min(content_bottom - 18, vessel_bottom + 58)
        for dx in (-int(vessel_r * 0.62), int(vessel_r * 0.62)):
            lx = cx + dx
            c.create_rectangle(lx - 8, vessel_bottom + 8, lx + 8, leg_bottom,
                               fill="#aeb8c1", outline=edge, width=1)
            c.create_line(lx - 3, vessel_bottom + 10, lx - 3, leg_bottom - 2,
                          fill="#e7ecef", width=3)
            c.create_oval(lx - 14, leg_bottom - 5, lx + 14, leg_bottom + 7,
                          fill=steel_light, outline=edge, width=1)

        # Vessel shell: layered highlights create depth without image assets.
        c.create_rectangle(vl, vessel_top, vr, vessel_bottom, fill=steel,
                           outline=edge, width=2)
        c.create_oval(vl, vessel_top - head_h, vr, vessel_top + head_h,
                      fill=steel_light, outline=edge, width=2)
        c.create_oval(vl, vessel_bottom - head_h, vr, vessel_bottom + head_h,
                      fill=steel_light, outline=edge, width=2)

        inner_l, inner_r = vl + 8, vr - 8
        inner_top, inner_bottom = vessel_top + 8, vessel_bottom - 8
        c.create_rectangle(inner_l, inner_top, inner_r, inner_bottom,
                           fill="#f9fbfc", outline="")
        # Brushed-steel highlights near the wall
        for frac, width_frac, col in [
            (0.05, 0.09, "#eef2f5"), (0.19, 0.07, "#d7dde3"),
            (0.73, 0.08, "#dde3e8"), (0.86, 0.07, "#b9c3cc"),
        ]:
            x1 = vl + int((2 * vessel_r) * frac)
            x2 = x1 + int((2 * vessel_r) * width_frac)
            c.create_rectangle(x1, vessel_top + 4, x2, vessel_bottom - 4,
                               fill=col, outline="")
        # Re-establish the process window over shell highlights.
        c.create_rectangle(inner_l, inner_top, inner_r, inner_bottom,
                           fill="#f9fbfc", outline="")

        # Liquid level and subtle depth.
        liq_y = vessel_top + int(vessel_h * 0.54)
        c.create_rectangle(inner_l, liq_y, inner_r, inner_bottom,
                           fill=liquid, outline="")
        c.create_oval(inner_l, liq_y - 8, inner_r, liq_y + 8,
                      fill="#dcefff", outline=liquid_edge, width=1)
        c.create_arc(inner_l, vessel_bottom - head_h, inner_r, vessel_bottom + 11,
                     start=180, extent=180, style="arc", outline="#91c6eb", width=1)

        # Decorative bubbles scale with vessel size.
        bubble_pos = [(.18,.64,2),(.30,.78,2),(.43,.68,1),(.55,.84,2),(.66,.73,2),(.78,.89,1),(.83,.63,1),(.40,.92,2)]
        for fx, fy, rr in bubble_pos:
            x = inner_l + int((inner_r-inner_l) * fx)
            y = vessel_top + int(vessel_h * fy)
            c.create_oval(x-rr, y-rr, x+rr, y+rr, fill="#ffffff", outline="#a9d4f1")

        # Redraw shell edges after liquid/window fills.
        c.create_line(vl, vessel_top, vl, vessel_bottom, fill=edge, width=2)
        c.create_line(vr, vessel_top, vr, vessel_bottom, fill=edge, width=2)
        c.create_arc(vl, vessel_top-head_h, vr, vessel_top+head_h,
                     start=0, extent=180, style="arc", outline=edge, width=2)
        c.create_arc(vl, vessel_bottom-head_h, vr, vessel_bottom+head_h,
                     start=180, extent=180, style="arc", outline=edge, width=2)

        # Agitator motor, shaft and impeller.
        motor_w = max(38, int(vessel_r * 0.34))
        motor_h = max(34, int(content_h * 0.075))
        motor_bottom = vessel_top - head_h + 3
        motor_top = max(content_top + 3, motor_bottom - motor_h - 18)
        c.create_rectangle(cx-motor_w/2, motor_top, cx+motor_w/2, motor_top+motor_h,
                           fill="#aeb8c1", outline=edge, width=2)
        c.create_oval(cx-motor_w/2-3, motor_top-7, cx+motor_w/2+3, motor_top+7,
                      fill=steel_light, outline=edge, width=1)
        rib_n = 5
        for i in range(1, rib_n):
            xx = cx - motor_w/2 + i * motor_w/rib_n
            c.create_line(xx, motor_top+5, xx, motor_top+motor_h-5, fill=steel_dark, width=1)
        c.create_rectangle(cx-12, motor_top+motor_h, cx+12, motor_bottom,
                           fill="#aab4bd", outline=edge, width=1)
        shaft_end = vessel_top + int(vessel_h * 0.84)
        c.create_line(cx, motor_bottom, cx, shaft_end, fill=edge, width=3)
        imp_y = vessel_top + int(vessel_h * 0.72)
        blade = int(vessel_r * 0.54)
        c.create_rectangle(cx-blade, imp_y-5, cx+blade, imp_y+5,
                           fill="#7d8994", outline=edge, width=1)
        tip = int(vessel_r * 0.18)
        c.create_polygon(cx-blade, imp_y-5, cx-blade-tip, imp_y-12,
                         cx-blade-tip, imp_y+2, cx-blade, imp_y+5,
                         fill="#aeb8c1", outline=edge)
        c.create_polygon(cx+blade, imp_y-5, cx+blade+tip, imp_y-12,
                         cx+blade+tip, imp_y+2, cx+blade, imp_y+5,
                         fill="#aeb8c1", outline=edge)
        c.create_rectangle(cx-7, imp_y-12, cx+7, imp_y+12,
                           fill="#aeb8c1", outline=edge, width=1)
        c.create_text(min(vr + 10, process_x1 - 50), imp_y, anchor="w", text="M-101",
                      fill=ink, font=("TkDefaultFont", 9, "bold"))

        # Top nozzles
        for frac in (-0.55, 0.55):
            nx = cx + int(vessel_r * frac)
            ny = vessel_top - head_h + 5
            c.create_rectangle(nx-7, ny-22, nx+7, ny, fill="#aeb8c1", outline=edge, width=1)
            c.create_oval(nx-11, ny-27, nx+11, ny-17, fill=steel_light, outline=edge, width=1)

        # Bottom drain
        c.create_rectangle(cx-8, vessel_bottom+head_h-3, cx+8, vessel_bottom+head_h+15,
                           fill="#aeb8c1", outline=edge, width=1)
        c.create_oval(cx-13, vessel_bottom+head_h+10, cx+13, vessel_bottom+head_h+20,
                      fill=steel_light, outline=edge, width=1)

        # Process line helper. Labels and y positions follow the vessel.
        line_start = process_x0 + 12
        def inlet(y_frac, label, color, dy=-15):
            y = vessel_top + int(vessel_h * y_frac)
            c.create_line(line_start, y, vl-10, y, fill=color, width=2,
                          arrow="last", arrowshape=(10, 12, 4))
            c.create_text(line_start+8, y+dy, anchor="w", text=label, fill=ink,
                          font=("TkDefaultFont", 9, "bold"))
            c.create_rectangle(vl-8, y-6, vl+5, y+6, fill=steel_light,
                               outline=edge, width=1)
            c.create_oval(vl-12, y-7, vl-4, y+7, fill="#aeb8c1", outline=edge, width=1)

        inlet(0.15, "P3 Feed", pipe)
        inlet(0.31, "P1 Ácido", acid)
        inlet(0.42, "P2 Base", base)
        inlet(0.54, "P4 Antiesp.", anti)
        inlet(0.84, "MFC gás\nAr / O₂", gas, dy=-25)

        # Exhaust with elbow; label remains inside the process region.
        ey = vessel_top + int(vessel_h * 0.08)
        elbow_x = min(process_x1 - 30, vr + max(36, int(process_w * 0.07)))
        c.create_rectangle(vr-5, ey-6, vr+7, ey+6, fill=steel_light, outline=edge, width=1)
        c.create_line(vr+7, ey, elbow_x, ey, fill=pipe, width=3)
        c.create_line(elbow_x, ey, elbow_x, ey-30, fill=pipe, width=3)
        c.create_line(elbow_x, ey-30, process_x1-8, ey-30, fill=pipe, width=3,
                      arrow="last", arrowshape=(10, 12, 4))
        c.create_text(max(vr+18, process_x1-170), ey-49, anchor="w",
                      text="PCV-101 / exaustão", fill=ink,
                      font=("TkDefaultFont", 8, "bold"))

        # Instrument bubbles between vessel and live panel.
        sensor_x = min(process_x1 - 28, vr + 34)
        sensors = [
            (0.20, "pH", "#1c5fa8"), (0.34, "DO", "#2e8b57"),
            (0.48, "T", "#c96f00"), (0.63, "Foam", "#00838f"),
            (0.78, "Pr", "#6a1b9a"),
        ]
        bubble_r = max(14, min(19, int(vessel_r * 0.13)))
        for fy, tag, color in sensors:
            sy = vessel_top + int(vessel_h * fy)
            c.create_line(vr, sy, sensor_x-bubble_r-3, sy, fill="#85929d",
                          dash=(3, 3), width=1)
            c.create_oval(sensor_x-bubble_r, sy-bubble_r,
                          sensor_x+bubble_r, sy+bubble_r,
                          fill="#ffffff", outline=color, width=2)
            c.create_text(sensor_x, sy, text=tag, fill=ink,
                          font=("TkDefaultFont", 8, "bold"))

        # The equipment identification is kept in the process-view header.
        # Avoid a second bottom caption competing visually with legs/shadow.

    def _recipe_ui(self):
        f=self.tabs["recipe"]
        txt=("Receita virtual padrão\n\n"
             "Fase 1 — Inóculo/adaptação: 0–2 h, sem alimentação, DO SP 35%\n"
             "Fase 2 — Crescimento batch: 2 h até início do feed, DO SP 30%\n"
             "Fase 3 — Fed-batch produção: após início do feed, DO SP 25%\n\n"
             "A estratégia de alimentação é selecionada no painel esquerdo:\n"
             "• Constante\n• Rampa linear\n• Exponencial\n• S-stat (PID)\n\n"
             "Na v3.0.0 a receita é automaticamente construída a partir do início de feed e tempo final.\n"
             "O JSON salvo preserva todos os parâmetros e configurações de processo.")
        t=tk.Text(f,wrap="word",font=("TkDefaultFont",11)); t.pack(fill="both",expand=True,padx=12,pady=12)
        t.insert("1.0",txt); t.configure(state="disabled")

    def load_defaults(self):
        d=defaults()
        for k,v in self.vars.items():
            if k not in d: continue
            if isinstance(v,tk.BooleanVar): v.set(bool(d[k]))
            else: v.set(str(d[k]))
        for v in self.sensor_fault_vars.values(): v.set("Normal")
        for v in self.act_fault_vars.values(): v.set("Normal")
        self.status.configure(text="Parâmetros padrão carregados.")

    def read_params(self):
        p=defaults()
        strk={"mode","feed_strategy","DO_strategy","recipe_name"}
        boolk={"control_T","control_pH","foam_control","pressure_control","trip_T_HH","trip_Pr_HH","trip_V_HH"}
        for k,v in self.vars.items():
            if k in strk: p[k]=v.get()
            elif k in boolk: p[k]=bool(v.get())
            else: p[k]=fnum(v.get(),p.get(k,0))
        if p["dt"]<=0 or p["tf"]<=0: raise ValueError("tf e dt devem ser positivos.")
        if p["dt"]>0.05: raise ValueError("Use dt <= 0,05 h para melhor estabilidade.")
        if p["V0"]<=0 or p["Vmax"]<p["V0"]: raise ValueError("Volumes inválidos.")
        return p

    def run_sim(self):
        if self.worker_thread is not None and self.worker_thread.is_alive():
            return
        try:
            self.p=self.read_params()
            sf={k:v.get() for k,v in self.sensor_fault_vars.items()}
            af={k:v.get() for k,v in self.act_fault_vars.items()}
        except Exception as e:
            LOG.exception("Falha ao preparar simulação")
            traceback.print_exc()
            messagebox.showerror("Erro",str(e))
            return

        self.cancel_event.clear()
        self.progress_var.set(0.0)
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status.configure(text="Simulando em worker thread...")
        self.worker_thread=threading.Thread(
            target=self._simulation_worker,
            args=(self.p,sf,af),
            daemon=True,
            name="BiofermentorSimulationWorker",
        )
        self.worker_thread.start()
        self.after(50,self._poll_worker_queue)

    def _simulation_worker(self,p,sf,af):
        try:
            sim=BiofermentorSimulator(p,sf,af)

            def progress_cb(fraction,time_h):
                self.worker_queue.put(("progress",float(fraction),float(time_h)))

            result=sim.run(
                progress_callback=progress_cb,
                cancel_check=self.cancel_event.is_set,
            )
            self.worker_queue.put(("done",result))
        except SimulationCancelled as exc:
            self.worker_queue.put(("cancelled",str(exc)))
        except Exception as exc:
            LOG.exception("Falha durante a simulação em worker thread")
            self.worker_queue.put(("error",exc,traceback.format_exc()))

    def _poll_worker_queue(self):
        finished=False
        try:
            while True:
                msg=self.worker_queue.get_nowait()
                kind=msg[0]
                if kind=="progress":
                    _,fraction,time_h=msg
                    self.progress_var.set(100.0*fraction)
                    self.status.configure(
                        text=f"Simulando... {100*fraction:5.1f}% | t={time_h:.2f} h"
                    )
                elif kind=="done":
                    self.result=msg[1]
                    self.progress_var.set(100.0)
                    self.plot_all()
                    self.show_metrics()
                    self.show_alarms()
                    self.draw_pid()
                    self.status.configure(text="Simulação concluída.")
                    finished=True
                elif kind=="cancelled":
                    self.status.configure(text=msg[1])
                    finished=True
                elif kind=="error":
                    _,exc,tb=msg
                    LOG.error(tb)
                    self.status.configure(text="Erro.")
                    messagebox.showerror("Erro",str(exc))
                    finished=True
        except queue.Empty:
            pass

        if finished:
            self.run_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.worker_thread=None
            return

        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.after(50,self._poll_worker_queue)
        else:
            # Defensive cleanup if a worker exits without a terminal message.
            self.run_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.worker_thread=None

    def cancel_sim(self):
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.cancel_event.set()
            self.status.configure(text="Solicitando cancelamento seguro...")

    def _style_axis(self, ax, title=None, xlabel=None, ylabel=None):
        if title:
            ax.set_title(title, fontsize=10, fontweight="bold", color="#17324d", pad=8)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        ax.set_facecolor("#fbfcfd")
        ax.grid(True, alpha=0.22, linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#a9b5bf")
        ax.spines["bottom"].set_color("#a9b5bf")
        ax.tick_params(labelsize=8, colors="#445666")

    def plot_all(self):
        r = self.result
        t, Y, M, U, A = r["t"], r["Y"], r["M"], r["U"], r["A"]

        self.fig_over.clear()
        ax = self.fig_over.add_subplot(221)
        ax.plot(t, Y[:,0], label="Xv", lw=1.8); ax.plot(t, Y[:,1], label="Xd", lw=1.5)
        self._style_axis(ax, "Biomassa", ylabel="g/L"); ax.legend(frameon=False, fontsize=8)
        ax = self.fig_over.add_subplot(222)
        ax.plot(t, Y[:,2], label="Glicose", lw=1.8); ax.plot(t, Y[:,3], label="Etanol", lw=1.8)
        self._style_axis(ax, "Substrato e produto", ylabel="g/L"); ax.legend(frameon=False, fontsize=8)
        ax = self.fig_over.add_subplot(223)
        ax.plot(t, M[:,2], label="DO", lw=1.8); ax.axhline(self.p["DO_sp"], ls="--", lw=1.2, label="SP")
        self._style_axis(ax, "Oxigênio dissolvido", xlabel="Tempo [h]", ylabel="% sat."); ax.legend(frameon=False, fontsize=8)
        ax = self.fig_over.add_subplot(224)
        ax.plot(t, Y[:,6], label="V", lw=1.8); ax.plot(t, Y[:,9], label="Foam", lw=1.5)
        self._style_axis(ax, "Volume e espuma", xlabel="Tempo [h]"); ax.legend(frameon=False, fontsize=8)
        self.fig_over.tight_layout(pad=2.0); self.can_over.draw()

        self.fig_bio.clear()
        ax = self.fig_bio.add_subplot(211)
        for j, label in [(0,"Xv"),(1,"Xd"),(2,"S"),(3,"EtOH"),(4,"N")]:
            ax.plot(t, Y[:,j], label=label, lw=1.6)
        self._style_axis(ax, "Estados biológicos e composição", ylabel="g/L")
        ax.legend(ncol=5, frameon=False, fontsize=8)
        ax = self.fig_bio.add_subplot(212)
        ax.plot(t, M[:,0], label="T", lw=1.7); ax.plot(t, M[:,1], label="pH", lw=1.7); ax.plot(t, M[:,2], label="DO %", lw=1.7)
        self._style_axis(ax, "Variáveis monitoradas", xlabel="Tempo [h]")
        ax.legend(frameon=False, fontsize=8)
        self.fig_bio.tight_layout(pad=2.0); self.can_bio.draw()

        self.fig_gas.clear()
        labs = [("OUR",6),("CER",7),("RQ",8),("kLa",5)]
        for i, (label, j) in enumerate(labs, 1):
            ax = self.fig_gas.add_subplot(2,2,i); ax.plot(t, A[:,j], lw=1.7)
            self._style_axis(ax, label, xlabel="Tempo [h]")
        self.fig_gas.tight_layout(pad=2.0); self.can_gas.draw()

        self.fig_ctrl.clear()
        labs = [("Feed [L/h]",0),("Ácido",1),("Base",2),("Antiesp.",3),("RPM",4),("Gás [vvm]",5),("O₂ fração",6),("Vent",7)]
        for i, (label, j) in enumerate(labs, 1):
            ax = self.fig_ctrl.add_subplot(4,2,i); ax.plot(t, U[:,j], lw=1.5)
            self._style_axis(ax, label, xlabel="Tempo [h]")
        self.fig_ctrl.tight_layout(pad=1.6); self.can_ctrl.draw()

        self.fig_kin.clear()
        labs = [("μ [1/h]",0),("qS total",2),("qS crescimento",11),("qS não-crescimento",12),
                ("qS fermentativo",14),("qS respiratório",15),("qP etanol",3),("stress N",18)]
        for i, (label, j) in enumerate(labs, 1):
            ax = self.fig_kin.add_subplot(4,2,i); ax.plot(t, A[:,j], lw=1.6)
            self._style_axis(ax, label, xlabel="Tempo [h]")
        self.fig_kin.tight_layout(pad=1.4); self.can_kin.draw()

    def show_alarms(self):
        for item in self.alarm_tree.get_children():
            self.alarm_tree.delete(item)

        rows = self.result["alarms"]
        trip = bool(self.result["trip"])
        if trip:
            self.alarm_status_var.set("TRIP ATIVO — " + str(self.result["trip_reason"]))
            self.alarm_status.configure(bg="#fde1e1", fg="#982a2a")
        elif rows:
            self.alarm_status_var.set(f"{len(rows)} evento(s) registrado(s); sem TRIP ativo")
            self.alarm_status.configure(bg="#fff3d6", fg="#705000")
        else:
            self.alarm_status_var.set("Nenhum alarme registrado na última simulação")
            self.alarm_status.configure(bg="#e1f0e5", fg="#245b36")

        for t, level, message in rows:
            lvl = str(level).upper()
            tag = "TRIP" if "TRIP" in lvl else ("ALARM" if "AL" in lvl else ("WARN" if "WARN" in lvl else ""))
            self.alarm_tree.insert("", "end", values=(f"{t:.3f}", level, message), tags=(tag,) if tag else ())

        if trip and not any("TRIP" in str(r[1]).upper() for r in rows):
            self.alarm_tree.insert("", "end", values=("—", "TRIP", self.result["trip_reason"]), tags=("TRIP",))

    def show_metrics(self):
        r=self.result; t=r["t"]; Y=r["Y"]; U=r["U"]; A=r["A"]; p=self.p
        Xv,Xd,S,P,N,CL,V,T,ph,Foam,Pr=Y[-1]
        feed=np.trapezoid(U[:,0],t)
        gin=p["S0"]*p["V0"]+np.trapezoid(U[:,0]*p["Sfeed"],t)
        gout=S*V; gcons=max(gin-gout,EPS)
        et=P*V-p["P0"]*p["V0"]
        yps=et/gcons
        prod=et/max(t[-1]*V,EPS)
        viab=100*Xv/max(Xv+Xd,EPS)
        txt=f"""Biofermentor Virtual SC v3.0.0 — RELATÓRIO DA BATELADA
================================================

Modo / estratégia          : {p['mode']} / {p['feed_strategy']}
Estratégia DO              : {p['DO_strategy']}
Tempo final                : {t[-1]:.3f} h
Volume final               : {V:.4f} L
Alimentação acumulada      : {feed:.4f} L

ESTADO FINAL
------------
X viável                   : {Xv:.4f} g/L
X morta                    : {Xd:.4f} g/L
Viabilidade                : {viab:.2f} %
Glicose                    : {S:.4f} g/L
Etanol                     : {P:.4f} g/L
Nitrogênio                 : {N:.4f} g/L
DO                         : {100*CL/max(SCProcess(p).oxygen_saturation(T,Pr,p['o2_base']),EPS):.2f} % sat.
Temperatura                : {T:.3f} °C
pH                         : {ph:.3f}
Espuma                     : {Foam:.3f}
Pressão                    : {Pr:.4f} bar(g)

DESEMPENHO
----------
Massa líquida de etanol    : {et:.4f} g
Glicose consumida          : {gcons:.4f} g
Yp/s observado             : {yps:.4f} g/g
Produtividade volumétrica  : {prod:.4f} g/L/h
Xv máximo                  : {np.max(Y[:,0]):.4f} g/L
Etanol máximo              : {np.max(Y[:,3]):.4f} g/L
DO mínimo                  : {np.min(r['M'][:,2]):.2f} %
μ máximo                   : {np.max(A[:,0]):.4f} 1/h
kd máximo                  : {np.max(A[:,1]):.4f} 1/h
OUR máximo                 : {np.max(A[:,6]):.3f}
CER máximo                 : {np.max(A[:,7]):.3f}
RQ médio                   : {np.mean(A[:,8]):.3f}

SEGURANÇA
---------
Alarmes registrados        : {len(r['alarms'])}
Trip                       : {'SIM - '+r['trip_reason'] if r['trip'] else 'não'}

INTEGRIDADE CIENTÍFICA
---------------------
Recuperação C fermentativa  : {r['parameter_audit']['carbon_recovery_nominal_ferm']:.3f}
Recuperação C respiratória  : {r['parameter_audit']['carbon_recovery_nominal_resp']:.3f}
Recup. C ferm. não-cresc.   : {r['parameter_audit']['carbon_recovery_nominal_ng_ferm']:.3f}
Status global               : {r['integrity_report']['overall_status']}
Carbono                      : {r['dynamic_carbon_audit']['status']}
Recuperação C dinâmica      : {r['dynamic_carbon_audit']['recovery_pct']:.2f} %
Erro balanço C dinâmico     : {r['dynamic_carbon_audit']['error_pct']:.2f} %
C residual                  : {r['dynamic_carbon_audit']['residual_gC']:.4f} gC
Nitrogênio                   : {r['dynamic_nitrogen_audit']['status']}
Recuperação N dinâmica      : {r['dynamic_nitrogen_audit']['recovery_pct']:.2f} %
Erro balanço N dinâmico     : {r['dynamic_nitrogen_audit']['error_pct']:.2f} %
N residual                  : {r['dynamic_nitrogen_audit']['residual_gN']:.4f} gN
Oxigênio                    : {r['dynamic_oxygen_audit']['status']}
Recuperação O2 dinâmica     : {r['dynamic_oxygen_audit']['recovery_pct']:.5f} %
Erro balanço O2 dinâmico    : {r['dynamic_oxygen_audit']['error_pct']:.5f} %
O2 residual                 : {r['dynamic_oxygen_audit']['residual_mgO2']:.5f} mg
Limiares                    : PASS ≤ {p['mass_balance_pass_abs_error_pct']:.1f}% | FAIL ≥ {p['mass_balance_fail_abs_error_pct']:.1f}%
Avisos de integridade       : {len(r['integrity_warnings'])}
{chr(10).join('  - '+x for x in r['integrity_warnings']) if r['integrity_warnings'] else '  Nenhum aviso automático.'}

NOTA
----
O modelo de pH usa capacidade tampão e fluxos equivalentes ácido/base; não é
uma especiação completa de eletrólitos. A correção de C* com temperatura é
empírica local. A v3.0 separa demanda de crescimento e catabolismo fermentativo não associado
ao crescimento; os parâmetros qS_ng_max/Kn_cat/N_cat_floor são fenomenológicos
e exigem calibração experimental. Para uso quantitativo, identifique parâmetros
com dados experimentais e valide em condições independentes.
"""
        self.metric_text.delete("1.0","end"); self.metric_text.insert("1.0",txt)

    def export_csv(self):
        if self.result is None:
            messagebox.showinfo("CSV","Execute uma simulação primeiro."); return
        fn=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],
                                        initialfile="biofermentor_virtual_v3_0_0_run.csv")
        if not fn:return
        r=self.result
        hdr=["t_h"]+["true_"+x for x in SCProcess.names]+ \
            ["meas_T","meas_pH","meas_DO_pct","meas_Pr","meas_Xv","meas_S","meas_P","meas_V","meas_Foam"]+ \
            ["u_"+x for x in BiofermentorSimulator.U_NAMES]+["aux_"+x for x in BiofermentorSimulator.A_NAMES]+["phase"]
        with open(fn,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(hdr)
            for i,t in enumerate(r["t"]):
                w.writerow([t,*r["Y"][i],*r["M"][i],*r["U"][i],*r["A"][i],r["phases"][i]])
        self.status.configure(text="CSV exportado: "+fn)

    def save_json(self):
        try:p=self.read_params()
        except Exception as e: LOG.exception("Erro ao ler parâmetros"); traceback.print_exc(); messagebox.showerror("Erro",str(e)); return
        data={"version":"3.0.0","params":p,
              "sensor_faults":{k:v.get() for k,v in self.sensor_fault_vars.items()},
              "actuator_faults":{k:v.get() for k,v in self.act_fault_vars.items()}}
        fn=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")],
                                        initialfile="biofermentor_virtual_recipe_v3_0_0.json")
        if not fn:return
        with open(fn,"w",encoding="utf-8") as f:json.dump(data,f,indent=2,ensure_ascii=False)
        self.status.configure(text="Receita salva: "+fn)

    def load_json(self):
        fn=filedialog.askopenfilename(filetypes=[("JSON","*.json"),("Todos","*.*")])
        if not fn:return
        try:
            with open(fn,"r",encoding="utf-8") as f:data=json.load(f)
            p=data.get("params",{})
            for k,v in self.vars.items():
                if k not in p:continue
                if isinstance(v,tk.BooleanVar):v.set(bool(p[k]))
                else:v.set(str(p[k]))
            for k,val in data.get("sensor_faults",{}).items():
                if k in self.sensor_fault_vars:self.sensor_fault_vars[k].set(val)
            for k,val in data.get("actuator_faults",{}).items():
                if k in self.act_fault_vars:self.act_fault_vars[k].set(val)
            self.status.configure(text="Receita carregada: "+fn)
        except Exception as e: LOG.exception("Erro ao carregar JSON"); traceback.print_exc(); messagebox.showerror("Erro ao carregar",str(e))



def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    App().mainloop()

if __name__ == "__main__":
    main()
