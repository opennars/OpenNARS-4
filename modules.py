import torch
import torch.nn as nn
import torch.nn.functional as F


class ResBlock(nn.Module):
    def __init__(self, in_channel, out_channel, stride = 1):
        super(ResBlock, self).__init__()
        self.left = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(out_channel)
        )
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channel != out_channel:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channel, out_channel, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channel)
            )

    def forward(self, x):
        out = self.left(x)
        out = out + self.shortcut(x)
        out = F.relu(out)

        return out


class FirstModule(nn.Module):
    def __init__(self):
        super(FirstModule, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        self.layer1 = ResBlock(64, 64, 1)
        self.layer2 = ResBlock(64, 64, 1)

    def forward(self, x):
        return self.layer2(self.layer1(self.conv1(x)))


class SecondModule(nn.Module):
    def __init__(self):
        super(SecondModule, self).__init__()
        self.layer1 = ResBlock(64, 128, 2)
        self.layer2 = ResBlock(128, 128, 2)

    def forward(self, x):
        return self.layer2(self.layer1(x))


class ThirdModule(nn.Module):
    def __init__(self):
        super(ThirdModule, self).__init__()
        self.layer1 = ResBlock(128, 256, 2)
        self.layer2 = ResBlock(256, 256, 2)

    def forward(self, x):
        tmp = F.avg_pool2d(self.layer2(self.layer1(x)), 2)
        tmp = tmp.view(tmp.size(0), -1)
        return tmp


class Final(nn.Module):
    def __init__(self):
        super(Final, self).__init__()
        self.fc = nn.Linear(1024, 10)

    def forward(self, x):
        return self.fc(x)


class Observer(nn.Module):
    def __init__(self):
        super(Observer, self).__init__()
        self.linear1 = nn.Linear(1024, 512)
        self.linear2 = nn.Linear(512, 256)

    def symbolic_embedding(self, x):
        return 1 / (1 + torch.exp(-100 * x))

    def forward(self, x):
        return self.symbolic_embedding(self.linear2(self.linear1(x)))

# tmp = torch.rand([1, 1, 28, 28])
# tmp = F.interpolate(tmp, scale_factor=2)
# m1 = FirstModule()
# m2 = SecondModule()
# m3 = ThirdModule()
# fc = Final()
# ob = Observer()
# a = m1(tmp)
# b = m2(a)
# c = m3(b)
# e = fc(c)
# f = ob(c)
#
# print(f.sum())
# print(f.shape)
