﻿using GoalSetting.Rules;
using System;
using System.Collections.ObjectModel;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Forms;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace GoalSetting.Views
{
    /// <summary>
    /// Interaction logic for RulePopUp.xaml
    /// </summary>
    public partial class RulePopUp : Window
    {
        private ObservableCollection<PARule> rules;

        public RulePopUp(ObservableCollection<PARule> rules)
        {
            this.InitializeComponent();
            this.rules = rules;
            AddRules();
        }

        internal void AddRules()
        {
            foreach (PARule rule in rules)
            {
                StackPanel container = new StackPanel();
                container.Background = new SolidColorBrush(Colors.LightGray);
                container.Orientation = System.Windows.Controls.Orientation.Horizontal;
                Thickness containerMargin = container.Margin;
                container.Height = 30;
                containerMargin.Bottom = 10;
                container.Margin = containerMargin;

                System.Windows.Controls.Image smiley = new System.Windows.Controls.Image();
                smiley.Height = 25;

                switch (rule.Progress)
                {
                    case Progress.VeryLow:
                        smiley.Source = BitmapToImageSource(Properties.Resources.smiley_5);
                        break;
                    case Progress.Low:
                        smiley.Source = BitmapToImageSource(Properties.Resources.smiley_4);
                        break;
                    case Progress.Average:
                        smiley.Source = BitmapToImageSource(Properties.Resources.smiley_3);
                        break;
                    case Progress.High:
                        smiley.Source = BitmapToImageSource(Properties.Resources.smiley_2);
                        break;
                    case Progress.VeryHigh:
                        smiley.Source = BitmapToImageSource(Properties.Resources.smiley_1);
                        break;
                }

                TextBlock text = new TextBlock();
                text.VerticalAlignment = VerticalAlignment.Center;
                text.Inlines.Add(rule.Title);
                Thickness margin = text.Margin;
                margin.Left = 20;
                text.Margin = margin;

                container.Children.Add(smiley);
                container.Children.Add(text);
                Rules.Children.Add(container);
            }

        }

        private BitmapImage BitmapToImageSource(Bitmap bitmap)
        {
            using (MemoryStream stream = new MemoryStream())
            {
                bitmap.Save(stream, ImageFormat.Png); // Was .Bmp, but this did not show a transparent background.

                stream.Position = 0;
                BitmapImage result = new BitmapImage();
                result.BeginInit();
                // According to MSDN, "The default OnDemand cache option retains access to the stream until the image is needed."
                // Force the bitmap to load right now so we can dispose the stream.
                result.CacheOption = BitmapCacheOption.OnLoad;
                result.StreamSource = stream;
                result.EndInit();
                result.Freeze();
                return result;

            }
        }

        public new bool? ShowDialog()
        {
            Screen mainScreen = Screen.AllScreens[0];

            foreach (Screen screen in Screen.AllScreens)
            {
                if (screen.WorkingArea.Size.Height >= mainScreen.WorkingArea.Size.Height && screen.WorkingArea.Width >= mainScreen.WorkingArea.Width)
                {
                    mainScreen = screen;
                }
            }

            this.Left = mainScreen.WorkingArea.Right - this.Width;
            this.Top = mainScreen.WorkingArea.Bottom - this.Height;

            return base.ShowDialog();
        }

    }
}
