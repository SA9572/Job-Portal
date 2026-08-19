import React, { useEffect, useState } from 'react';
import {
  X,
  Check,
  Zap,
  Sparkles,
  ShieldCheck,
  Crown,
  Building2,
  ArrowRight,
  Loader2,
} from 'lucide-react';
import { subscriptionApi } from '../services/api';
import { SubscriptionPlan } from '../types/api';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (planId: string) => void;
}

export const UpgradeModal: React.FC<UpgradeModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('yearly');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    subscriptionApi
      .getPlans()
      .then((res) => {
        setPlans(res.plans);
        const popular = res.plans.find((p) => p.popular);
        if (popular) setSelectedPlanId(popular.id);
      })
      .catch((err) => {
        console.error('Failed to load plans', err);
      })
      .finally(() => setLoading(false));
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCheckout = async (planId: string) => {
    if (planId === 'free') {
      onClose();
      return;
    }

    setProcessingId(planId);
    setSuccessMessage(null);

    try {
      const res = await subscriptionApi.checkout({
        plan_id: planId,
        billing_cycle: billingCycle,
      });

      setSuccessMessage(`🎉 Success! Transaction ${res.transaction_id}. Welcome to Pro!`);
      if (onSuccess) onSuccess(planId);
      setTimeout(() => {
        onClose();
        setSuccessMessage(null);
      }, 2500);
    } catch (err: any) {
      console.error('Checkout failed', err);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fadeIn">
      <div className="relative max-h-[90vh] w-full max-w-5xl overflow-y-auto rounded-3xl border border-[#e4e8de] bg-[#fbf8ee] p-6 md:p-8 shadow-2xl text-[#0b2319]">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 rounded-full border border-slate-200 bg-white p-2 text-slate-500 hover:bg-slate-100 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#d2e2c2] bg-[#e3edd9] px-4 py-1 text-xs font-extrabold text-[#225738] mb-3">
            <Sparkles className="h-4 w-4 text-[#2e7d52]" /> Supercharge Your Career Hunt
          </div>
          <h2 className="text-2xl md:text-4xl font-extrabold text-[#0a2618] tracking-tight">
            Unlock Full AI Matching &amp; Real-Time Ingestion
          </h2>
          <p className="mt-2 text-xs md:text-sm text-slate-600 font-medium">
            Get instant match scoring, unlimited job alerts, priority candidate highlighting, and direct recruiter links.
          </p>

          {/* Billing Cycle Toggle */}
          <div className="mt-6 inline-flex items-center gap-2 rounded-full border border-[#e4e8de] bg-white p-1.5 shadow-sm">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`rounded-full px-5 py-2 text-xs font-extrabold transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-[#2e7d52] text-white shadow'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Monthly Billing
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`flex items-center gap-1.5 rounded-full px-5 py-2 text-xs font-extrabold transition-all ${
                billingCycle === 'yearly'
                  ? 'bg-[#2e7d52] text-white shadow'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Annual Billing
              <span className="rounded-full bg-[#e3edd9] px-2 py-0.5 text-[10px] font-extrabold text-[#1e5a39]">
                SAVE 20%
              </span>
            </button>
          </div>
        </div>

        {/* Success Alert */}
        {successMessage && (
          <div className="mb-6 rounded-2xl border border-[#c4dbb4] bg-[#e3edd9] p-4 text-center text-xs font-extrabold text-[#1e5a39]">
            {successMessage}
          </div>
        )}

        {/* Loading Skeleton */}
        {loading ? (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {[1, 2, 3].map((n) => (
              <div
                key={n}
                className="h-96 rounded-2xl border border-[#e4e8de] bg-white p-6 animate-pulse"
              />
            ))}
          </div>
        ) : (
          /* Plan Cards Grid */
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3 items-stretch">
            {plans.map((plan) => {
              const isPopular = plan.popular;
              const isSelected = selectedPlanId === plan.id;
              const price =
                billingCycle === 'yearly'
                  ? (plan.price_yearly / 12).toFixed(0)
                  : plan.price_monthly.toFixed(0);

              return (
                <div
                  key={plan.id}
                  onClick={() => setSelectedPlanId(plan.id)}
                  className={`relative flex flex-col justify-between rounded-2xl border p-6 transition-all duration-300 cursor-pointer bg-white ${
                    isPopular
                      ? 'border-[#2e7d52] ring-2 ring-[#2e7d52] shadow-lg scale-[1.02]'
                      : 'border-[#e4e8de] hover:border-[#2e7d52]'
                  }`}
                >
                  {/* Badge */}
                  {plan.badge && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-[#2e7d52] px-3.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-white shadow-md">
                      {plan.badge}
                    </div>
                  )}

                  <div>
                    {/* Header */}
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-extrabold text-[#0a2618] flex items-center gap-2">
                        {plan.id === 'pro' && <Crown className="w-4 h-4 text-[#2e7d52]" />}
                        {plan.id === 'enterprise' && <Building2 className="w-4 h-4 text-emerald-700" />}
                        {plan.name}
                      </h3>
                    </div>

                    <p className="mt-2 text-xs text-slate-500 font-medium min-h-[36px]">{plan.description}</p>

                    {/* Price */}
                    <div className="my-4 flex items-baseline gap-1">
                      <span className="text-4xl font-extrabold text-[#0a2618]">${price}</span>
                      <span className="text-xs font-semibold text-slate-500">/month</span>
                      {billingCycle === 'yearly' && plan.price_yearly > 0 && (
                        <span className="ml-auto text-[10px] text-slate-400 font-bold">
                          Billed ${plan.price_yearly}/yr
                        </span>
                      )}
                    </div>

                    <div className="my-4 border-t border-slate-100" />

                    {/* Feature List */}
                    <ul className="space-y-2.5">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-xs text-slate-700 font-semibold">
                          <Check className="h-4 w-4 text-[#2e7d52] shrink-0 mt-0.5" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* CTA Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCheckout(plan.id);
                    }}
                    disabled={processingId === plan.id}
                    className={`mt-8 w-full flex items-center justify-center gap-2 rounded-xl py-3 text-xs font-extrabold transition-all shadow ${
                      isPopular
                        ? 'btn-green-gradient'
                        : plan.id === 'free'
                        ? 'btn-light-secondary'
                        : 'btn-green-gradient'
                    }`}
                  >
                    {processingId === plan.id ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" /> Processing...
                      </>
                    ) : plan.id === 'free' ? (
                      'Continue with Free'
                    ) : (
                      <>
                        Upgrade to {plan.name} <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Footer Guarantee */}
        <div className="mt-8 pt-6 border-t border-slate-200 flex flex-wrap items-center justify-between text-xs text-slate-600 font-semibold gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>30-Day Money-Back Guarantee &bull; Cancel Anytime</span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium">Instant activation. Secure 256-bit SSL encrypted checkout.</p>
        </div>
      </div>
    </div>
  );
};
