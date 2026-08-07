import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class PNLIOSymbioticSim:
    def __init__(self, size=100, creativity=0.05, seed=42):
        np.random.seed(seed)
        self.size = size
        self.grid = np.random.rand(size, size) * 0.2
        self.memory = self.grid.copy()
        self.creativity = creativity
        self.tau, self.theta, self.C = [], [], []

    def entropy(self):
        p = self.grid.flatten()
        p = p / (p.sum() + 1e-12)
        p = p[p > 0]
        return -np.sum(p * np.log2(p))

    def step(self):
        neighbors = (
            np.roll(self.grid, 1, 0) + np.roll(self.grid, -1, 0) +
            np.roll(self.grid, 1, 1) + np.roll(self.grid, -1, 1)
        ) / 4
        mutation = np.random.normal(
            0,
            self.creativity * (1 + np.std(neighbors)),
            self.grid.shape
        )
        before = self.entropy()
        self.grid = np.clip(
            0.65 * neighbors +
            0.25 * self.memory +
            mutation,
            0, 1
        )
        self.memory = 0.95 * self.memory + 0.05 * self.grid
        after = self.entropy()
        self.tau.append(len(self.tau) + 1)
        self.theta.append(after)
        self.C.append(after - before)

    def run(self, steps=300):
        for _ in range(steps):
            self.step()


if __name__ == "__main__":
    sim = PNLIOSymbioticSim(size=100, creativity=0.05, seed=42)
    sim.run(300)

    print(f"Theta final: {sim.theta[-1]:.6f}")
    print(f"C media: {np.mean(sim.C):.6f}")
    print(f"Theta inicial: {sim.theta[0]:.6f}")
    print(f"Delta theta total: {sim.theta[-1] - sim.theta[0]:.6f}")
    print(f"Grid min: {sim.grid.min():.4f}, max: {sim.grid.max():.4f}, mean: {sim.grid.mean():.4f}")

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('PNLIO SymbioticSim - Co-creacion Humano-IA (Memoria + Mutacion adaptativa)',
                 fontsize=16, fontweight='bold')

    ax1 = plt.subplot(2, 3, 1)
    im1 = ax1.imshow(sim.grid, cmap='plasma', interpolation='nearest', vmin=0, vmax=1)
    ax1.set_title('Estado final Lattis (Simbiosis)')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    ax2 = plt.subplot(2, 3, 2)
    im2 = ax2.imshow(sim.memory, cmap='magma', interpolation='nearest', vmin=0, vmax=1)
    ax2.set_title('Memoria Estructural (95% persistencia)')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(sim.tau, sim.theta, color='#2E86AB', linewidth=1.5)
    ax3.set_title('theta - Entropia de Shannon [bits]')
    ax3.set_xlabel('tau [pasos]')
    ax3.set_ylabel('bits')
    ax3.grid(True, alpha=0.3)

    ax4 = plt.subplot(2, 3, 4)
    ax4.plot(sim.tau, sim.C, color='#A23B72', linewidth=0.8, alpha=0.8)
    ax4.axhline(y=np.mean(sim.C), color='#F18F01', linestyle='--', alpha=0.7,
                label=f'Media: {np.mean(sim.C):.6f}')
    ax4.set_title(f'C = Delta theta/Delta tau - Media: {np.mean(sim.C):.6f}')
    ax4.set_xlabel('tau [pasos]')
    ax4.set_ylabel('bits/paso')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    ax5 = plt.subplot(2, 3, 5)
    diff = sim.grid - sim.memory
    im5 = ax5.imshow(diff, cmap='RdBu_r', interpolation='nearest', vmin=-0.5, vmax=0.5)
    ax5.set_title('Innovacion = Grid - Memoria')
    plt.colorbar(im5, ax=ax5, fraction=0.046, pad=0.04)

    ax6 = plt.subplot(2, 3, 6)
    grad_x, grad_y = np.gradient(sim.grid)
    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    im6 = ax6.imshow(gradient_magnitude, cmap='viridis', interpolation='nearest')
    ax6.set_title('Gradientes (Entrelazamiento)')
    plt.colorbar(im6, ax=ax6, fraction=0.046, pad=0.04)

    plt.tight_layout()
    filename = 'pnlio_symbiotic_sim.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Guardado: {filename}")
