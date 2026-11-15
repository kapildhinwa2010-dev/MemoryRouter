import pytest
import torch
from memoryrouter import MemoryRouter, create_memoryrouter

class TestMemoryRouter:
    def test_init(self):
        m = MemoryRouter(dim=256, hidden_dim=512)
        assert m.dim == 256
    
    def test_forward(self):
        m = MemoryRouter(dim=256)
        x = torch.randn(32, 256)
        assert m(x).shape == (32, 256)
    
    def test_factory(self):
        m = create_memoryrouter()
        assert isinstance(m, MemoryRouter)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
