import torch
import torch.nn as nn
import torch.nn.functional as F


class VanillaVAE(nn.Module):
    def __init__(self, in_channels=1, latent_dim=32, hidden_dims=[32, 64, 128, 256, 512]):
        super(VanillaVAE, self).__init__()
        self.image_chennels = in_channels
        self.latent_dim = latent_dim

        # Encoder
        encoder_modules = []
        for h_dim in hidden_dims:
            encoder_modules.append(
                nn.Sequential(
                    nn.Conv2d(in_channels, h_dim, kernel_size=3, stride=2, padding=1),
                    nn.BatchNorm2d(h_dim),
                    nn.ReLU())
            )
            in_channels = h_dim
        encoder_modules.append(nn.Flatten(start_dim=1))
        self.encoder = nn.Sequential(*encoder_modules)
        self.fc_mu = nn.Linear(hidden_dims[-1]*16, latent_dim)
        self.fc_var = nn.Linear(hidden_dims[-1]*16, latent_dim)

        # Decoder
        decoder_modules = []
        self.decoder_input = nn.Linear(latent_dim, hidden_dims[-1]*16)
        hidden_dims.reverse()
        for h_dim in hidden_dims[1:]:
            decoder_modules.append(
                nn.Sequential(
                    nn.ConvTranspose2d(in_channels, h_dim, 
                                       kernel_size=3, stride=2, padding=1, output_padding=1),
                    nn.BatchNorm2d(h_dim),
                    nn.ReLU())
            )
            in_channels = h_dim
        decoder_modules.append(
            nn.Sequential(
                nn.ConvTranspose2d(hidden_dims[-1], self.image_chennels,
                                   kernel_size=3, stride=2, padding=5, output_padding=1),
                nn.Sigmoid())
        )
        self.decoder = nn.Sequential(*decoder_modules)

    def encode(self, inputs):
        r"""Encodes the input by passing through the encoder network
            and returns the latent codes.
        Args:
            inputs: (Tensor) Input tensor to encoder [N x C x H x W]
        Returns: (Tensor)
            Mean and standard deviation of the latent Gaussian distribution
        """
        result = self.encoder(inputs)               # [N x 512 x 4 x 4]
        result = torch.flatten(result, start_dim=1) # [N x 8192]
        
        return self.fc_mu(result), self.fc_var(result)
    
    def decode(self, z):
        r"""Maps the given latent codes onto the image space.
        Args:
            z: (Tensor) [B x D] Hidden states
        Returns: (Tensor) [B x C x H x W]
        """
        result = self.decoder_input(z)
        result = result.view(-1, 512, 4, 4)
        result = self.decoder(result)
        return result

    def reparameterize(self, mu, log_var):
        r"""Reparameterization trick to sample from N(mu, var) from N(0,1).
        Args:
            mu: (Tensor) Mean of the latent Gaussian [B x D]
            stddev: (Tensor) Standard deviation of the latent Gaussian [B x D]
        :return: (Tensor) [B x D]
        """
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return eps * std + mu

    def forward(self, inputs):
        mu, log_var = self.encode(inputs)
        z = self.reparameterize(mu, log_var)
        return  self.decode(z), mu, log_var

    def loss_fn(self, recons, inputs, mu, log_var, **kwargs):
        r"""Computes the VAE loss function. 
            KL(N(\mu, \sigma), N(0, 1)) = 
            \log \frac{1}{\sigma} + \frac{\sigma^2 + \mu^2}{2} - \frac{1}{2}
        """
#         kld_weight = kwargs['M_N'] # Account for the minibatch samples from the dataset
        recons_loss = F.mse_loss(recons, inputs)
#         recons_loss = F.binary_cross_entropy(recons, inputs)
        KLD = torch.mean(-0.5 * torch.sum(1 + log_var - mu**2 - log_var.exp(), dim=1), dim=0)
        loss = recons_loss - KLD
        return loss, recons_loss, KLD
#         return {'loss': loss, 'reconstruction_loss': recons_loss, 'KL-divergence': kld}

    def sample(self, num_samples, current_device, **kwargs):
        r"""Samples from the latent space and return the corresponding image space map.
        Args:
            num_samples: (Int) Number of samples
            current_device: (Int) Device to run the model
        :return: (Tensor)
        """
        z = torch.randn(num_samples, self.latent_dim)
        z = z.to(current_device)
        samples = self.decode(z)

        return samples

    def generate(self, x):
        r"""Given an input image x, returns the reconstructed image
        Args:
            x: (Tensor) [B x C x H x W]
        Returns:
            Reconstructed image (Tensor) [B x C x H x W]
        """
        return self.forward(x)[0]