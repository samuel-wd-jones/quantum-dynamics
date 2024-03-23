# About
#   Example code to produce an animation demonstrating Damped Rabi Oscillations with varying Laser Detuning


# Imports
from qdlib import *


# Initialisation
#   Change
rf = 1e8    # Rabi Frequency
dr = rf / 5 # Decay Rate
DURATION = 10

#   Leave
lds = np.linspace(-5 * rf, 5 * rf, 600)
os.system(f'mkdir "{LOCAL_DIR}/dro_ld_cache" 2>/dev/null')
os.system(f'mkdir "{LOCAL_DIR}/dro_ld_frames" 2>/dev/null')


# Main
#   Generate or load results
try:
    with open(f"{LOCAL_DIR}/dro_ld_cache/{min(lds)}_{max(lds)}_{len(lds)}.pickle", "rb") as r:
        results = pickle.load(r)
    print("Cache found")
except FileNotFoundError:
    results = []
    for i, ld in enumerate(lds):
        print(f"\rNo cache, generating: {100 * i / len(lds):.2f}%", end="")
        results.append(atomic_qubits_evolution(rf, dr, ld))
    print("\r" + " "*os.get_terminal_size().columns + "\rData generated", end="")
    with open(f"{LOCAL_DIR}/dro_ld_cache/{min(lds)}_{max(lds)}_{len(lds)}.pickle", "wb") as wf:
        pickle.dump(results, wf)
    print("\r" + " "*os.get_terminal_size().columns + "\rData cached")

#   Plot each frame
os.system(f'rm "{LOCAL_DIR}/dro_ld_frames/*" 2>/dev/null')
secondary = [r[1][1][-1] for r in results]
for i, result in enumerate(results):
    print(f"\rGenerating frames: {100 * i / len(results):.2f}%", end="")
    plt.figure(figsize=(7.5, 3), layout="tight")
    plt.axis("off")

    plt.plot(result[2] / np.max(result[2]), result[1][1], color="black")
    plt.plot(np.linspace(1.5, 2.5, len(results)), secondary, color="black", ls="--")
    plt.plot([1, 1.5 + i / (len(results) - 1)], [secondary[i] for _ in range(2)], color="black", ls=":")

    [plt.plot([x, x], [0, 1], color="black", alpha=.1) for x in [0, .33, .67, 1, 1.5, 1.83, 2.17, 2.5]]
    [plt.plot([0, 2.5], [y, y], color="black", alpha=.1) for y in [0, .5]]
    [plt.scatter(0, y, color="black", marker="_") for y in [0, .5, 1]]
    [plt.scatter(x, 0, color="black", marker="|") for x in [0, .33, .67, 1, 1.5, 1.83, 2.17, 2.5]]
    plt.plot([1.1, 1.1, 1.4, 1.4, 1.1], [.65, .85, .85, .65, .65], color="black", alpha=.5)
    [plt.annotate(ob[0], (ob[1], ob[2]), va="center", ha="center") for ob in [
        ["0     ", 0, 0],
        ["$\\rho_{11}(t)$    0.5                     ", 0, .5],
        ["1     ", 0, 1],
        ["0", 0, -.06],
        [f"{str(20 * np.pi / rf)[:4]}", 1, -.06],
        [f"{str(.33 * 20 * np.pi / rf)[:4]}", .33, -.06],
        [f"{str(.67 * 20 * np.pi / rf)[:4]}", .67, -.06],
        ["\n$t$ $(s \\cdot 10^{-7})$", .5, -.1],
        [f"{lds[0] / rf:.1f}", 1.5, -.06],
        [f"{lds[int(len(lds) * .33)] / rf:.1f}", 1.83, -.06],
        [f"{lds[int(len(lds) * .67)] / rf:.1f}", 2.17, -.06],
        [f"{lds[-1] / rf:.1f}", 2.5, -.06],
        ["\n$\\Delta / \\Omega$", 2, -.1],
        [f"$\\Delta / \\Omega$\n${lds[i] / rf:.1f}$" + " "*3*int(lds[i] < 0), 1.25, .75]
    ]]

    plt.xlim([0 -.1, 2.5 +.1])
    plt.ylim([0 -.1, 1 +.1])
    plt.savefig(f"{LOCAL_DIR}/dro_ld_frames/{i:010}.png")
    plt.close()
print("\r" + " "*os.get_terminal_size().columns + "\rFrames generated")

# Stitch Frames
os.system(f'ffmpeg -y -f image2 -framerate {max(int(len(lds) / DURATION), 1)} -pattern_type glob -i "{LOCAL_DIR}/dro_ld_frames/*.png" "{LOCAL_DIR}/dro_ld.mp4"')