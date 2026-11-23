
# Mobile app references

## How to use
1. Name the screen or flow and its one job: "sign up with phone OTP", "add an expense in under 5 seconds".
2. Pick one real app from "Apps to study" that does the same job well. Look at the whole flow, not only one screen. Note gestures, haptics and what happens on back.
3. Search the galleries for more variants of the same flow.
4. For the platform: follow iOS patterns on iOS (see `design-engineering/apple-design`) and Material patterns on Android, unless the brand has its own system.
5. Build with the right skill: `flutter-app` (Flutter), `motion/animate-expo` (React Native/Expo), `write-swift` (Swift), `mobile-native` (web app on a phone). Use `motion/gestures` for drag and sheets.
6. Make a mockup first for app UI (see `mockup-before-build`).
7. Copy the flow and the quality bar. Do not copy the brand, icons or illustrations.

## Apps to study
| App | Study it for |
|---|---|
| Things 3 (culturedcode.com/things) | Calm lists, quick add, delightful small details |
| Linear mobile | Dense lists made calm, swipe actions |
| Arc Search | Gestures, playful transitions |
| Revolut, Monzo, Wise | Money flows, onboarding with KYC, card controls |
| CRED, Zerodha Kite | Indian fintech: premium motion (CRED), fast plain trading UI (Kite) |
| Duolingo | Onboarding before sign-up, streaks, mascot feedback, gamification |
| Headspace | Calm onboarding, soft illustration |
| Airbnb | Search, filters, maps, listing detail |
| Swiggy, Zomato | Delivery: location, cart, live order tracking |
| Oura, Whoop | Health data shown simply on a phone |
| Apple apps (Weather, Wallet, Fitness) | Platform-perfect motion and type |

## Galleries
| Site | Use it for |
|---|---|
| [60fps](https://60fps.design/) | 2,000+ animation clips from the best apps; the main source for app motion and transitions |
| [Collect UI](https://collectui.com/) | Hand-picked app interfaces by screen type |
| [Dribbble](https://dribbble.com/) | Search the exact screen: "onboarding app", "wallet app". Concepts only |
| [Godly](https://godly.design/) | Web, app and UI design, hand-picked |
| [Bencho Finds](https://bencho.dev/finds) | UI interaction clips |
| [details.so](https://www.details.so/inspo) | Small transitions and micro-interactions |
| [Mobbin](https://mobbin.com/) (not on the source list) | Real iOS and Android flows by app, screen and pattern |

## App icons and store
| Site | Use it for |
|---|---|
| [Icon Museum](https://icon.museum/) | Beautiful iOS app icons |
| [Iconly](https://iconly.design/) | 2,400+ app and web icons |
| [Godly logos](https://godly.design/logos/) | Marks that also work as app icons |
| [Posts.design](https://posts.design/) | Social posts from 460+ brands, for launch and store visuals |
| [Open Source UI](https://opensourceui.in/components) | Device mockups for store screens and the landing page |

## Motion and sound for apps
| Site | Use it for |
|---|---|
| [Kinetics](https://kinetics.colorion.co) | Bouncy, natural-feeling animations with prompts |
| [Amicro loaders](https://amicro.vercel.app/loaders) | Loaders and micro-transitions |
| [uisfx](https://uisfx.com) | 936 free interface sounds in 12 styles |
| [Cuelume](https://cuelume-site.pages.dev/) | Click and hover sounds |

## Mobile app landing pages
Use `landing-page-inspiration`. Good app pages there: culturedcode.com/things, amie.so, arc.net, duolingo.com, headspace.com, monzo.com.

## Rules
- Thumb first: main actions in the bottom half of the screen.
- Every tap gets feedback within 100 ms (press state or haptic).
- Respect safe areas, the system back gesture and dynamic type.
- Test on a real mid-range Android phone, not only an iPhone or a simulator.
- Sounds are off by default unless the app's job is playful.
