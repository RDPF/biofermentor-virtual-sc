import os,sys,subprocess,json

def test_identifiability_cli_generates_reproducible_artifacts(project_root,tmp_path):
    env=os.environ.copy(); env["PYTHONPATH"]=str(project_root/"src")
    cmd=[sys.executable,"-m","biofermentor.identifiability_report",
         "--output-dir",str(tmp_path),"--tf","2","--dt","0.02",
         "--parameters","mu_max","Ks","Yxs","Yps",
         "--outputs","X_total","S","P"]
    p=subprocess.run(cmd,cwd=project_root,env=env,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert (tmp_path/"IDENTIFIABILITY_REPORT.md").exists()
    assert (tmp_path/"IDENTIFIABILITY_RESULTS.json").exists()
    assert (tmp_path/"SENSITIVITY_RANKING.csv").exists()
    q=subprocess.run(cmd+["--check"],cwd=project_root,env=env,capture_output=True,text=True)
    assert q.returncode==0,q.stdout+q.stderr
    r=json.loads((tmp_path/"IDENTIFIABILITY_RESULTS.json").read_text(encoding="utf-8"))
    assert r["analysis_type"]=="local_sensitivity_and_practical_identifiability"
