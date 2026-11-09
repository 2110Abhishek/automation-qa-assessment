import json
import os
import unittest
import urllib.request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestPulseQAArtifacts(unittest.TestCase):
    def test_task1_pdf_exists_and_valid(self):
        pdf_path = os.path.join(BASE_DIR, "Task1_QA_Report_Abhishek.pdf")
        self.assertTrue(os.path.exists(pdf_path), "Task 1 PDF report missing")
        self.assertGreater(os.path.getsize(pdf_path), 50000, "PDF size unexpectedly small")
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            self.assertEqual(header, b"%PDF-", "File is not a valid PDF")

    def test_task2_workflow_schema(self):
        wf_path = os.path.join(BASE_DIR, "Task2", "Task2_Workflow_Abhishek.json")
        self.assertTrue(os.path.exists(wf_path), "Task 2 JSON missing")
        with open(wf_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertEqual(data.get("name"), "Task2_Workflow_Abhishek")
        nodes = {n["name"]: n for n in data.get("nodes", [])}
        self.assertIn("Schedule Trigger (Hourly)", nodes)
        self.assertIn("Fetch Popular Repositories", nodes)
        self.assertIn("Filter & Select Top 5 Repositories", nodes)
        self.assertIn("Fetch Top Repo README (Enrichment)", nodes)
        self.assertIn("Decode & Process README Preview", nodes)
        self.assertIn("Evaluate Star Threshold (IF Node)", nodes)

        # Verify all connections point to valid node names
        connections = data.get("connections", {})
        for src_node, targets in connections.items():
            self.assertIn(src_node, nodes, f"Source node '{src_node}' not found in nodes list")
            for conn_type, routes in targets.items():
                for target_route in routes:
                    for conn in target_route:
                        self.assertIn(conn["node"], nodes, f"Target node '{conn['node']}' not found in nodes list")

    def test_bonus_workflow_schema(self):
        wf_path = os.path.join(BASE_DIR, "Bonus", "Bonus_UptimeMonitor_Abhishek.json")
        self.assertTrue(os.path.exists(wf_path), "Bonus JSON missing")
        with open(wf_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertEqual(data.get("name"), "Bonus_UptimeMonitor_Abhishek")
        nodes = {n["name"]: n for n in data.get("nodes", [])}
        self.assertIn("Schedule Trigger (Every 5 Min)", nodes)
        self.assertIn("Primary Health Check (Ping)", nodes)
        self.assertIn("Calculate Latency & Health Check", nodes)
        self.assertIn("Is Application Healthy (200 OK)?", nodes)
        self.assertIn("Wait 5 Seconds (Retry Buffer)", nodes)
        self.assertIn("Retry Probe (Second Attempt)", nodes)

        connections = data.get("connections", {})
        for src_node, targets in connections.items():
            self.assertIn(src_node, nodes, f"Source node '{src_node}' not found in nodes list")
            for conn_type, routes in targets.items():
                for target_route in routes:
                    for conn in target_route:
                        self.assertIn(conn["node"], nodes, f"Target node '{conn['node']}' not found in nodes list")

    def test_screenshots_valid_png(self):
        pngs = [
            os.path.join(BASE_DIR, "screenshots", "workflow.png"),
            os.path.join(BASE_DIR, "screenshots", "execution.png"),
            os.path.join(BASE_DIR, "screenshots", "uptime-workflow.png"),
        ]
        for p in pngs:
            self.assertTrue(os.path.exists(p), f"Screenshot {p} does not exist")
            self.assertGreater(os.path.getsize(p), 10000, f"Screenshot {p} unexpectedly small")
            with open(p, "rb") as f:
                sig = f.read(8)
                self.assertEqual(sig, b"\x89PNG\r\n\x1a\n", f"File {p} is not a valid PNG")

    def test_loom_docs_exist(self):
        loom_link = os.path.join(BASE_DIR, "Loom", "demo-link.txt")
        loom_script = os.path.join(BASE_DIR, "Loom", "VIDEO_WALKTHROUGH_SCRIPT.md")
        self.assertTrue(os.path.exists(loom_link), "Loom demo link file missing")
        self.assertTrue(os.path.exists(loom_script), "Loom script missing")

if __name__ == "__main__":
    unittest.main()
