"""
奇幻冒险RPG - 音乐管理器
生成背景音乐和音效（使用程序化音频合成）
"""

import numpy as np
import struct
import wave
import os

class MusicGenerator:
    """程序化音乐生成器"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.output_dir = "assets/audio"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_sine_wave(self, frequency, duration, volume=0.3):
        """生成正弦波"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave_data = np.sin(2 * np.pi * frequency * t) * volume
        return wave_data
    
    def generate_square_wave(self, frequency, duration, volume=0.2):
        """生成方波（8位风格）"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave_data = np.sign(np.sin(2 * np.pi * frequency * t)) * volume
        return wave_data
    
    def apply_envelope(self, wave_data, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
        """应用ADSR包络"""
        total_samples = len(wave_data)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        envelope = np.concatenate([
            np.linspace(0, 1, attack_samples),
            np.linspace(1, sustain, decay_samples),
            np.ones(max(0, sustain_samples)) * sustain,
            np.linspace(sustain, 0, release_samples)
        ])
        
        # 确保长度匹配
        if len(envelope) < total_samples:
            envelope = np.pad(envelope, (0, total_samples - len(envelope)), 'constant')
        elif len(envelope) > total_samples:
            envelope = envelope[:total_samples]
        
        return wave_data * envelope
    
    def create_bgm_town(self, filename="bgm_town.wav"):
        """生成城镇背景音乐 - 轻松愉快的旋律"""
        duration = 30  # 30秒循环
        
        # 和弦进行: C - Am - F - G
        chords = [
            [261.63, 329.63, 392.00],  # C大调
            [220.00, 277.18, 329.63],  # A小调
            [349.23, 440.00, 523.25],  # F大调
            [392.00, 493.88, 587.33]   # G大调
        ]
        
        melody_notes = [
            (261.63, 0.5), (329.63, 0.5), (392.00, 1.0),  # C E G
            (349.23, 0.5), (329.63, 0.5), (293.66, 1.0),  # F E D
            (261.63, 0.5), (293.66, 0.5), (349.23, 1.0),  # C D F
            (329.63, 0.5), (293.66, 0.5), (261.63, 2.0),  # E D C (长)
            (349.23, 0.5), (392.00, 0.5), (440.00, 1.0),  # F G A
            (392.00, 0.5), (349.23, 0.5), (329.63, 1.0),  # G F E
            (293.66, 0.5), (261.63, 0.5), (293.66, 1.0),  # D C D
            (261.63, 0.5), 0, (220.00, 2.0)              # C (休止) A (长)
        ]
        
        # 生成和弦背景
        chord_duration = duration / len(chords)
        bgm = np.zeros(int(self.sample_rate * duration))
        
        for i, chord in enumerate(chords):
            start_sample = int(i * chord_duration * self.sample_rate)
            for freq in chord:
                note = self.generate_sine_wave(freq, chord_duration, 0.08)
                note = self.apply_envelope(note, 0.3, 0.2, 0.6, 0.3)
                end_sample = min(start_sample + len(note), len(bgm))
                bgm[start_sample:end_sample] += note[:end_sample-start_sample]
        
        # 添加旋律
        current_time = 0
        for note_freq, note_dur in melody_notes:
            if note_freq > 0:
                note = self.generate_sine_wave(note_freq, note_dur, 0.15)
                note = self.apply_envelope(note, 0.05, 0.1, 0.7, 0.2)
                start_sample = int(current_time * self.sample_rate)
                end_sample = min(start_sample + len(note), len(bgm))
                bgm[start_sample:end_sample] += note[:end_sample-start_sample]
            current_time += note_dur
        
        # 归一化
        bgm = bgm / np.max(np.abs(bgm)) * 0.6
        
        # 保存为WAV
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, bgm)
        print(f"已生成城镇BGM: {filepath}")
        return filepath
    
    def create_bgm_battle(self, filename="bgm_battle.wav"):
        """生成战斗背景音乐 - 紧张激昂"""
        duration = 25
        
        bgm = np.zeros(int(self.sample_rate * duration))
        
        # 战斗鼓点节奏
        bpm = 140
        beat_interval = 60 / bpm
        
        for i in range(int(duration / beat_interval)):
            if i % 2 == 0:  # 强拍
                kick = self.generate_sine_wave(60, 0.15, 0.4)
                kick = self.apply_envelope(kick, 0.01, 0.1, 0.3, 0.1)
                start = int(i * beat_interval * self.sample_rate)
                end = min(start + len(kick), len(bgm))
                bgm[start:end] += kick[:end-start]
            
            if i % 4 == 2:  # 弱拍军鼓
                snare = self.generate_square_wave(200, 0.1, 0.15)
                snare = self.apply_envelope(snare, 0.001, 0.05, 0.2, 0.05)
                start = int(i * beat_interval * self.sample_rate)
                end = min(start + len(snare), len(bgm))
                bgm[start:end] += snare[:end-start]
        
        # 紧张的贝斯线
        bass_notes = [65.41, 73.42, 82.41, 87.31] * 8  # C D# F# G
        note_dur = beat_interval * 2
        
        for i, freq in enumerate(bass_notes):
            note = self.generate_sine_wave(freq, note_dur, 0.12)
            note = self.apply_envelope(note, 0.05, 0.15, 0.6, 0.1)
            start = int(i * note_dur * self.sample_rate)
            end = min(start + len(note), len(bgm))
            bgm[start:end] += note[:end-start]
        
        # 激昂的旋律（电吉他风格）
        melody = [
            (196.00, 0.2), (246.94, 0.2), (293.66, 0.2),  # B D G
            (293.66, 0.2), (246.94, 0.2), (196.00, 0.2),
            (220.00, 0.3), (261.63, 0.3), (329.63, 0.3),  # A C E
            (329.63, 0.2), (293.66, 0.2), (261.63, 0.2),
            (246.94, 0.4), 0, (220.00, 0.4),             # B (休止) A
            (196.00, 0.2), (220.00, 0.2), (246.94, 0.2),
            (261.63, 0.4), (293.66, 0.4), (349.23, 0.4)   # C D F A
        ]
        
        current_time = 0
        for note_freq, note_dur in melody:
            if note_freq > 0:
                # 使用失真效果（叠加谐波）
                note = self.generate_sine_wave(note_freq, note_dur, 0.06)
                note2 = self.generate_sine_wave(note_freq * 2, note_dur, 0.03)
                note3 = self.generate_square_wave(note_freq * 0.5, note_dur, 0.02)
                note = note + note2 + note3
                note = self.apply_envelope(note, 0.02, 0.1, 0.7, 0.15)
                
                start = int(current_time * self.sample_rate)
                end = min(start + len(note), len(bgm))
                bgm[start:end] += note[:end-start]
            current_time += note_dur
        
        # 归一化
        bgm = bgm / np.max(np.abs(bgm)) * 0.7
        
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, bgm)
        print(f"已生成战斗BGM: {filepath}")
        return filepath
    
    def create_bgm_field(self, filename="bgm_field.wav"):
        """生成野外探索BGM - 宁静自然"""
        duration = 32
        
        bgm = np.zeros(int(self.sample_rate * duration))
        
        # 自然环境音（柔和的风声）
        noise = np.random.uniform(-0.03, 0.03, len(bgm))
        # 低通滤波效果（简化版）
        for i in range(1, len(noise)):
            noise[i] = noise[i] * 0.02 + noise[i-1] * 0.98
        bgm += noise
        
        # 柔和的竖琴/钢琴分解和弦
        arpeggios = [
            [261.63, 329.63, 392.00, 523.25],  # Cmaj7
            [220.00, 277.18, 329.63, 440.00],  # Am7
            [174.61, 220.00, 261.63, 349.23],  # Fmaj7
            [196.00, 246.94, 293.66, 392.00]   # G7
        ]
        
        arp_duration = duration / len(arpeggios)
        
        for i, arp in enumerate(arpeggios):
            for j, freq in enumerate(arp):
                note_start = i * arp_duration + j * (arp_duration / 4)
                note = self.generate_sine_wave(freq, arp_duration / 4 * 0.9, 0.07)
                note = self.apply_envelope(note, 0.1, 0.2, 0.5, 0.4)
                
                start = int(note_start * self.sample_rate)
                end = min(start + len(note), len(bgm))
                if start < len(bgm):
                    bgm[start:end] += note[:min(len(note), len(bgm)-start)]
        
        # 长笛旋律
        flute_melody = [
            (523.25, 1.5), (587.33, 0.5), (659.25, 1.0),  # C5 E5 G5
            (587.33, 0.5), (523.25, 1.0), (493.88, 1.5),  # E5 C5 B4
            (440.00, 0.5), (493.88, 0.5), (523.25, 2.0),  # A4 B4 C5
            (587.33, 1.0), (659.25, 1.0), (587.33, 1.0),  # E5 G5 E5
            (523.25, 1.5), (493.88, 0.5), (440.00, 1.5),  # C5 B4 A4
            (392.00, 0.5), (440.00, 1.0), (493.88, 2.0)   # G4 A4 B4
        ]
        
        current_time = 2  # 延迟进入
        for note_freq, note_dur in flute_melody:
            note = self.generate_sine_wave(note_freq, note_dur, 0.05)
            # 添加颤音效果
            vibrato = np.sin(2 * np.pi * 5 * np.linspace(0, note_dur, len(note))) * 2
            note = np.interp(
                np.arange(len(note)) + vibrato,
                np.arange(len(note)),
                note
            )
            note = self.apply_envelope(note, 0.15, 0.2, 0.6, 0.3)
            
            start = int(current_time * self.sample_rate)
            end = min(start + len(note), len(bgm))
            if start < len(bgm):
                bgm[start:end] += note[:min(len(note), len(bgm)-start)]
            current_time += note_dur
        
        # 归一化
        bgm = bgm / np.max(np.abs(bgm)) * 0.55
        
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, bgm)
        print(f"已生成野外BGM: {filepath}")
        return filepath
    
    def create_sfx_attack(self, filename="sfx_attack.wav"):
        """生成攻击音效"""
        duration = 0.3
        
        # 剑击声 - 白噪声 + 低频冲击
        sfx = np.random.uniform(-1, 1, int(self.sample_rate * duration))
        
        # 快速衰减包络
        envelope = np.exp(-np.linspace(0, 15, len(sfx)))
        sfx = sfx * envelope * 0.4
        
        # 添加低频"重量感"
        impact = self.generate_sine_wave(80, 0.15, 0.3)
        impact = self.apply_envelope(impact, 0.001, 0.05, 0.3, 0.08)
        
        sfx[:len(impact)] += impact
        
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, sfx)
        print(f"已生成攻击音效: {filepath}")
        return filepath
    
    def create_sfx_magic(self, filename="sfx_magic.wav"):
        """生成魔法音效"""
        duration = 0.8
        
        # 魔法上升音
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # 频率从低到高滑动
        freq_start = 200
        freq_end = 1200
        freq = freq_start + (freq_end - freq_start) * (t / duration) ** 2
        
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        sfx = np.sin(phase) * 0.25
        
        # 添加泛音
        sfx += np.sin(phase * 2) * 0.1
        sfx += np.sin(phase * 3) * 0.05
        
        # 包络
        sfx = self.apply_envelope(sfx, 0.1, 0.2, 0.6, 0.3)
        
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, sfx)
        print(f"已生成魔法音效: {filepath}")
        return filepath
    
    def create_sfx_hit(self, filename="sfx_hit.wav"):
        """生成受击音效"""
        duration = 0.2
        
        # 沉闷的打击声
        sfx = self.generate_sine_wave(100, duration, 0.35)
        sfx += self.generate_square_wave(60, duration, 0.15)
        sfx = self.apply_envelope(sfx, 0.001, 0.03, 0.2, 0.1)
        
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, sfx)
        print(f"已生成受击音效: {filepath}")
        return filepath
    
    def create_sfx_victory(self, filename="sfx_victory.wav"):
        """生成胜利音效 - 短胜利旋律"""
        notes = [
            (523.25, 0.15),  # C5
            (659.25, 0.15),  # E5
            (783.99, 0.15),  # G5
            (1046.50, 0.4)   # C6 (高八度)
        ]
        
        sfx = np.array([])
        for freq, dur in notes:
            note = self.generate_sine_wave(freq, dur, 0.2)
            note = self.apply_envelope(note, 0.01, 0.05, 0.7, 0.15)
            sfx = np.concatenate([sfx, note])
        
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, sfx)
        print(f"已生成胜利音效: {filepath}")
        return filepath
    
    def create_sfx_levelup(self, filename="sfx_levelup.wav"):
        """生成升级音效"""
        notes = [
            (392.00, 0.12),  # G4
            (493.88, 0.12),  # B4
            (587.33, 0.12),  # D5
            (783.99, 0.12),  # G5
            (987.77, 0.35)   # B5
        ]
        
        sfx = np.array([])
        for freq, dur in notes:
            note = self.generate_sine_wave(freq, dur, 0.18)
            note2 = self.generate_sine_wave(freq * 2, dur, 0.08)  # 高频泛音
            note = note + note2
            note = self.apply_envelope(note, 0.005, 0.04, 0.75, 0.12)
            sfx = np.concatenate([sfx, note])
        
        filepath = os.path.join(self.output_dir, filename)
        self.save_wav(filepath, sfx)
        print(f"已生成升级音效: {filepath}")
        return filepath
    
    def save_wav(self, filepath, audio_data):
        """保存为WAV文件"""
        # 转换为16位整数格式
        audio_int = (audio_data * 32767).astype(np.int16)
        
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)   # 16位
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int.tobytes())
    
    def generate_all_audio(self):
        """生成所有音频资源"""
        print("开始生成游戏音频资源...")
        
        assets = {
            "bgm_town": self.create_bgm_town(),
            "bgm_battle": self.create_bgm_battle(),
            "bgm_field": self.create_bgm_field(),
            "sfx_attack": self.create_sfx_attack(),
            "sfx_magic": self.create_sfx_magic(),
            "sfx_hit": self.create_sfx_hit(),
            "sfx_victory": self.create_sfx_victory(),
            "sfx_levelup": self.create_sfx_levelup()
        }
        
        print("\n所有音频资源生成完成！")
        return assets


if __name__ == "__main__":
    generator = MusicGenerator()
    assets = generator.generate_all_audio()
    
    print("\n生成的文件列表:")
    for name, path in assets.items():
        print(f"  {name}: {path}")
