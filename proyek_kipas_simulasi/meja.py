#!/usr/bin/env python3
"""Simulasi rencana eksperimen video kipas. Tidak mengendalikan hardware."""
import argparse, csv, itertools, json, sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Pasang dependensi: python -m pip install pyyaml")
    raise SystemExit(2)

def load_settings(path):
    with open(path, encoding="utf-8") as f:
        c = yaml.safe_load(f) or {}
    e, fan, light = c.get("experiment", {}), c.get("fan", {}), c.get("light", {})
    cap, sim, out = c.get("capture", {}), c.get("simulation", {}), c.get("output", {})
    pwm, levels, reps = fan.get("pwm_values"), light.get("levels"), e.get("repetitions")
    if not isinstance(pwm, list) or not pwm or any(type(x) is not int or not 0 <= x <= 255 for x in pwm):
        raise ValueError("fan.pwm_values harus berupa daftar integer 0..255.")
    if not isinstance(levels, list) or not levels or any(type(x) is not int for x in levels):
        raise ValueError("light.levels harus berupa daftar integer.")
    if type(reps) is not int or reps < 1:
        raise ValueError("experiment.repetitions harus integer >= 1.")
    duration = float(cap.get("recording_seconds", 5))
    discard = float(cap.get("discard_first_seconds", 1))
    fps = float(cap.get("fps", 10))
    overhead = float(sim.get("transition_seconds", 0.5))
    if duration <= 0 or discard < 0 or discard >= duration or fps <= 0 or overhead < 0:
        raise ValueError("Periksa durasi, discard, fps, dan transition_seconds.")
    return c, pwm, levels, reps, duration, discard, fps, overhead, out

def main():
    p = argparse.ArgumentParser(description="Simulasi eksperimen kecepatan kipas")
    p.add_argument("--simulasi", choices=["jalankan"], required=True)
    p.add_argument("config", help="Path file konfigurasi YAML")
    a = p.parse_args()
    try:
        c, pwm, lights, reps, duration, discard, fps, overhead, out = load_settings(a.config)
        conditions = []
        for i, (fan, lamp, rep) in enumerate(itertools.product(pwm, lights, range(1, reps+1)), 1):
            conditions.append({
                "condition_id": i, "fan_pwm": fan, "light_level": lamp,
                "repetition": rep, "recording_seconds": duration,
                "discard_first_seconds": discard, "usable_seconds": duration-discard,
                "fps": fps, "planned_video_name": f"condition_{i:03d}.mp4"
            })
        total = len(conditions)
        estimate = total * (duration + overhead)
        root = Path(out.get("root", "data/simulasi"))
        session = root / f"{out.get('session_prefix', 't17')}_{datetime.now():%Y%m%d_%H%M%S}"
        session.mkdir(parents=True, exist_ok=False)
        with (session / "conditions.csv").open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(conditions[0]))
            w.writeheader(); w.writerows(conditions)
        summary = {
            "mode": "SIMULASI", "total_conditions": total, "pwm_values": pwm,
            "light_levels": lights, "repetitions": reps, "recording_seconds": duration,
            "discard_first_seconds": discard, "usable_seconds": duration-discard,
            "fps": fps, "transition_seconds": overhead,
            "estimated_duration_seconds": estimate,
            "estimated_duration_minutes": round(estimate/60, 2),
            "room_light_state": c.get("session", {}).get("room_light_state", "belum ditentukan"),
            "warning": "Tidak mengendalikan hardware dan tidak merekam video."
        }
        (session / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        with (session / "simulation_log.txt").open("w", encoding="utf-8") as log:
            def emit(s):
                print(s); log.write(s + "\n")
            emit("="*55)
            emit("SIMULASI EKSPERIMEN TAKSIRAN KECEPATAN KIPAS")
            emit(f"PWM: {pwm} | Lampu: {lights} | Pengulangan: {reps}")
            emit(f"Total kondisi: {total}")
            emit(f"Rekaman/kondisi: {duration:g} detik; buang awal: {discard:g} detik")
            emit(f"Estimasi durasi: {estimate/60:.1f} menit")
            emit("-"*55)
            for row in conditions:
                emit(f"[{row['condition_id']:03d}/{total}] PWM={row['fan_pwm']:3d} LIGHT={row['light_level']:3d} REP={row['repetition']:02d}")
            emit("-"*55)
            emit("SIMULATION COMPLETED - SUCCESS")
            emit(f"Folder sesi: {session.resolve()}")
            emit("Berkas: conditions.csv, summary.json, simulation_log.txt")
            emit("PERINGATAN: simulasi saja; tidak ada perangkat dikendalikan/video direkam.")
        print(f"\nValidasi: {total} kondisi; estimasi {estimate/60:.1f} menit.")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
