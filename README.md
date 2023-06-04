

# WIP 🚧

This is an attempt to find the best combination of weights for N strategies forming a portfolio, optimising for omega ratio.
The idea is based on [this](https://cs.uwaterloo.ca/~yuying/Courses/CS870_2012/Omega_paper_Short_Cm.pdf) paper, and it can certainly
be solved way easier using LP. This is just a fun experiment to use PSO to search for the weights.

Here's how it looks for 5 strategies where the portfoliovisualizer.com shows an omega ratio of 81.
![alt text](https://github.com/CojocaruDr/OmegaOptimizer/blob/main/ss.png?raw=true)

The PSO finds an omega ratio of 210, because it doesn't make the weights add up to 100%. That's essentially using leverage
and not considering the loses. Will fix soon.